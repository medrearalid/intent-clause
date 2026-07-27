const users = new Map([["member@example.test", "demo-hash"]]);

export function authenticate(email, passwordHash) {
  const storedHash = users.get(email);
  return storedHash !== undefined && storedHash === passwordHash;
}
