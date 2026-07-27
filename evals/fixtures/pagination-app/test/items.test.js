import assert from "node:assert/strict";
import test from "node:test";

import { listItems } from "../src/items.js";

test("lists all items by default", () => {
  assert.deepEqual(listItems(["a", "b", "c"]), ["a", "b", "c"]);
});
