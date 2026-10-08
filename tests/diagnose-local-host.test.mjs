import test from 'node:test';
import assert from 'node:assert/strict';
import { summarizeStatus, classifyError } from '../scripts/diagnose-local-host.mjs';

test('approved connection with no private ticket remains distinguishable', () => {
  assert.deepEqual(summarizeStatus({ stage: 'approved', ticket: null }, 200),
    { httpStatus: 200, stage: 'approved', joinTicketPresent: false, parentIdentityPresent: false });
});
test('diagnostics disclose presence only, never credential or remote payload bytes', () => {
  const ticket = 'x'.repeat(64);
  const output = JSON.stringify(summarizeStatus({ stage: 'approved', ticket, parentId: 'a'.repeat(36), token: 'private-token', receipt: 'private-receipt' }, 200));
  assert.equal(JSON.parse(output).joinTicketPresent, true);
  for (const secret of [ticket, 'private-token', 'private-receipt']) assert.equal(output.includes(secret), false);
  const hostile = JSON.stringify(summarizeStatus({ stage: 'private-token' }, 401));
  assert.equal(hostile.includes('private-token'), false);
  assert.equal(classifyError({ code: 'private-token', message: 'private-ticket' }), 'CHECK_FAILED');
  assert.equal(classifyError({ code: 'ECONNREFUSED', message: 'private-ticket' }), 'ECONNREFUSED');
});
