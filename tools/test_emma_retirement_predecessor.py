"""Execute the exact historical five-owner suite against its own old checkout.

This is historical regression evidence only, never current UI/review evidence.
Requires full git history and installed repo QA dependencies; fails closed.
"""
from pathlib import Path
import hashlib,subprocess,sys,tempfile,unittest
ROOT=Path(__file__).resolve().parents[1]
BASE='63fafd9594949160f912b3c1ca0e39b52432df34'
TEST_SHA='50c355865f779e7dc791542f5e2349332b140946b14c25547f58eca837570c76'
class HistoricalSuite(unittest.TestCase):
 def test_exact_predecessor_suite(self):
  with tempfile.TemporaryDirectory(prefix='emma-historical-checkout-') as tmp:
   target=Path(tmp)/'tree';added=False
   try:
    subprocess.run(['git','worktree','add','--detach',str(target),BASE],cwd=ROOT,check=True,stdout=subprocess.PIPE,stderr=subprocess.PIPE);added=True
    self.assertEqual(subprocess.check_output(['git','rev-parse','HEAD'],cwd=target,text=True).strip(),BASE)
    self.assertEqual(hashlib.sha256((target/'tools/test_emma_story_consumers.py').read_bytes()).hexdigest(),TEST_SHA)
    subprocess.run([sys.executable,'-m','unittest','discover','-s','tools','-p','test_emma_story_consumers.py'],cwd=target,check=True)
   finally:
    if added:subprocess.run(['git','worktree','remove','--force',str(target)],cwd=ROOT,check=True,stdout=subprocess.PIPE,stderr=subprocess.PIPE)
if __name__=='__main__':unittest.main()
