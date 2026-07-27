export function listItems(items, offset = 0, limit = items.length) {
  return items.slice(offset, offset + limit);
}
