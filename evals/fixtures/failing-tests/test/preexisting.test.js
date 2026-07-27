import assert from "node:assert/strict";
import test from "node:test";

test("pre-existing unrelated failure", () => {
  assert.equal("legacy-output", "expected-output");
});
