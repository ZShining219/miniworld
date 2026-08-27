export function moveItem<Item>(items: Item[], from: number, to: number): Item[] {
  if (
    from === to
    || from < 0
    || to < 0
    || from >= items.length
    || to >= items.length
  ) {
    return [...items]
  }

  const reordered = [...items]
  const [item] = reordered.splice(from, 1)
  reordered.splice(to, 0, item)
  return reordered
}

export function hasSameOrder(left: string[], right: string[]): boolean {
  return left.length === right.length && left.every((id, index) => id === right[index])
}
