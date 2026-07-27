import assert from "node:assert/strict";
import test from "node:test";

import { authenticate } from "../src/auth.js";

test("accepts a matching credential hash", () => {
  assert.equal(authenticate("member@example.test", "demo-hash"), true);
});

test("rejects an unknown account", () => {
  assert.equal(authenticate("missing@example.test", "demo-hash"), false);
});
