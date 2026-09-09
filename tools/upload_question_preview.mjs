import assert from 'node:assert/strict';
import { readFile, writeFile, appendFile } from 'node:fs/promises';
import { execFile } from 'node:child_process';
import { promisify } from 'node:util';
import { fileURLToPath } from 'node:url';

const execute = promisify(execFile);
const root = fileURLToPath(new URL('../', import.meta.url));
const worker = 'focuschrist-groq-proxy';
const alias = 'question-review';
const uploadArgs = ['versions', 'upload', '--preview-alias', alias, '--config', 'wrangler.toml'];

function activeDeployment(payload) {
  assert.equal(payload?.success, true, 'Deployment lookup did not succeed');
  const active = payload.result?.deployments?.[0];
  assert.ok(typeof active?.id === 'string' && active.id.length > 0, 'No active production deployment found');
  assert.ok(Array.isArray(active.versions) && active.versions.length > 0, 'Active deployment version traffic is unavailable');
  const versions = active.versions.map(version => {
    assert.ok(typeof version.version_id === 'string' && version.version_id.length > 0);
    assert.ok(Number.isFinite(version.percentage));
    return {version_id:version.version_id, percentage:version.percentage};
  }).sort((a,b)=>a.version_id.localeCompare(b.version_id));
  assert.equal(versions.reduce((sum,version)=>sum+version.percentage,0),100, 'Unexpected traffic allocation');
  return {id:active.id,versions};
}

async function readActiveDeployment(account, token) {
  const response = await fetch(`https://api.cloudflare.com/client/v4/accounts/${account}/workers/scripts/${worker}/deployments`, {
    method:'GET', redirect:'error', headers:{Authorization:`Bearer ${token}`}, signal:AbortSignal.timeout(20000)
  });
  assert.ok(response.ok, `Deployment lookup failed with HTTP ${response.status}`);
  return activeDeployment(await response.json());
}

function previewReceipt(output) {
  const version = output.match(/(?:Worker\s+)?Version ID:\s*([0-9a-f-]{36})/i)?.[1];
  const urls = output.match(/https:\/\/[a-z0-9.-]+\.workers\.dev\/?/gi) || [];
  const previewUrl = urls.find(value => new URL(value).hostname.startsWith(`${alias}-${worker}.`));
  assert.ok(version, 'Upload completed without a recognizable version receipt');
  assert.ok(previewUrl, 'Upload completed without the requested preview alias URL');
  return {version, previewUrl};
}

function selfTest() {
  const payload = {success:true,result:{deployments:[{id:'active',versions:[{version_id:'old',percentage:100}]}]}};
  const before = activeDeployment(payload);
  assert.deepEqual(activeDeployment(structuredClone(payload)),before);
  const changed = structuredClone(payload); changed.result.deployments[0].versions[0].version_id='new';
  assert.throws(()=>assert.deepEqual(activeDeployment(changed),before));
  assert.throws(()=>activeDeployment({success:true,result:{deployments:[]}}));
  assert.throws(()=>previewReceipt('https://focuschrist-groq-proxy.example.workers.dev'));
  assert.equal(previewReceipt('Worker Version ID: 11111111-1111-4111-8111-111111111111\nhttps://question-review-focuschrist-groq-proxy.example.workers.dev').version,'11111111-1111-4111-8111-111111111111');
  assert.deepEqual(uploadArgs,['versions','upload','--preview-alias','question-review','--config','wrangler.toml']);
  console.log('PASS: preview-only command, missing-state rejection and active deployment change detection.');
}

async function main() {
  assert.equal(process.env.GITHUB_EVENT_NAME,'pull_request','Only a pull-request event may upload a preview');
  const event = JSON.parse(await readFile(process.env.GITHUB_EVENT_PATH,'utf8'));
  assert.equal(event.pull_request?.head?.repo?.full_name,process.env.GITHUB_REPOSITORY,'Fork previews are not permitted');
  assert.equal(event.pull_request?.head?.ref,'fix/followup-evidence-retrieval','Unexpected preview branch');
  const head = event.pull_request.head.sha;
  assert.match(head,/^[0-9a-f]{40}$/);
  const checkout = await execute('git',['rev-parse','HEAD'],{cwd:root});
  assert.equal(checkout.stdout.trim(),head,'Checkout differs from the exact PR head');
  const token = process.env.CLOUDFLARE_API_TOKEN;
  const account = process.env.CLOUDFLARE_ACCOUNT_ID;
  assert.ok(token && account,'Existing Cloudflare repository secrets are required');
  assert.match(account,/^[a-f0-9]{32}$/i,'Invalid account identifier');
  const installed = JSON.parse(await readFile(new URL('../groq-proxy/node_modules/wrangler/package.json',import.meta.url),'utf8'));
  assert.equal(installed.version,'4.126.0','Preview tooling must match the reviewed lockfile version');
  const before = await readActiveDeployment(account,token);
  const receipt = {head,worker,productionBefore:before,productionUnchanged:false};
  let failed = false;
  try {
    const result = await execute(process.execPath,[fileURLToPath(new URL('../groq-proxy/node_modules/wrangler/bin/wrangler.js',import.meta.url)),...uploadArgs],{
      cwd:fileURLToPath(new URL('../groq-proxy/',import.meta.url)),
      env:{...process.env,CI:'true',WRANGLER_SEND_METRICS:'false'},timeout:300000,maxBuffer:2*1024*1024
    });
    Object.assign(receipt,previewReceipt(result.stdout));
  } catch (error) {
    // Only categorical flags leave the process; never expose provider text or credentials.
    const failureText = String(error?.stderr || '') + String(error?.stdout || '');
    receipt.uploadFailure = { cpuMention: /cpu/i.test(failureText), freePlanMention: /free/i.test(failureText), paidPlanMention: /paid/i.test(failureText), limitMention: /limit/i.test(failureText), authenticationMention: /authentication|unauthorized/i.test(failureText) };
    console.error(JSON.stringify({uploadFailure:receipt.uploadFailure}));
    failed = true;
  } finally {
    try {
      const after = await readActiveDeployment(account,token);
      receipt.productionAfter = after;
      assert.deepEqual(after,before,'Active production deployment changed during preview upload');
      receipt.productionUnchanged = true;
    } finally {
      await writeFile(new URL('../question-preview-receipt.json',import.meta.url),JSON.stringify(receipt,null,2)+'\n');
    }
  }
  assert.equal(failed,false,'Preview upload or receipt parsing failed; production comparison saved separately');
  console.log(JSON.stringify(receipt));
  if (process.env.GITHUB_STEP_SUMMARY) await appendFile(process.env.GITHUB_STEP_SUMMARY,
    `Preview version: ${receipt.version}\n\nPreview URL: ${receipt.previewUrl}\n\nExact PR head: ${head}\n\nProduction deployment unchanged: ${receipt.productionUnchanged}\n`);
}

if (process.argv.includes('--self-test')) selfTest();
else main().catch(error=>{ console.error(error?.name === 'AssertionError' ? error.message.split('\n')[0] : 'Preview operation failed; inspect the non-secret receipt.'); process.exitCode=1; });
