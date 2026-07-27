import assert from "node:assert/strict";
import test from "node:test";

import { total } from "../src/total.js";

test("reported bug: discounts should be applied", () => {
  assert.equal(total([10, -2]), 10);
});
