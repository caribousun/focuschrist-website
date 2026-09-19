#!/usr/bin/env node
'use strict';
const fs = require('node:fs');
const crypto = require('node:crypto');
const {validate} = require('./core');
const [reviewPath, assetPath, rejectedPath] = process.argv.slice(2);
if (!reviewPath || !assetPath) {
  console.error('Usage: node tools/anatomy-review/audit.js review.json image.png [rejected-hashes.json]');
  process.exitCode = 2;
} else {
  try {
    const review = JSON.parse(fs.readFileSync(reviewPath, 'utf8').replace(/^\uFEFF/, ''));
    const rejected = rejectedPath ? JSON.parse(fs.readFileSync(rejectedPath, 'utf8').replace(/^\uFEFF/, '')) : [];
    const actual = crypto.createHash('sha256').update(fs.readFileSync(assetPath)).digest('hex');
    const result = validate(review, Array.isArray(rejected) ? rejected : rejected.images || []);
    if (actual !== String(review.candidate?.sha256 || '').toLowerCase()) result.errors.push('The review describes different image bytes. Re-review this exact candidate.');
    result.status = result.errors.length ? 'blocked' : 'ready_for_visual_review';
    console.log(JSON.stringify({...result,actual_sha256:actual},null,2));
    process.exitCode = result.errors.length ? 1 : 0;
  } catch (error) {
    console.error('Anatomy review could not be verified: ' + error.message);
    process.exitCode = 2;
  }
}
