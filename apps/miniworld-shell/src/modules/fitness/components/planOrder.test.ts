import { describe, expect, it } from 'vitest'
import { hasSameOrder, moveItem } from './planOrder'

describe('fitness plan ordering', () => {
  const plans = ['胸', '背', '肩', '臀腿']

  it('moves an item up, down, or across multiple positions', () => {
    expect(moveItem(plans, 2, 1)).toEqual(['胸', '肩', '背', '臀腿'])
    expect(moveItem(plans, 1, 2)).toEqual(['胸', '肩', '背', '臀腿'])
    expect(moveItem(plans, 0, 3)).toEqual(['背', '肩', '臀腿', '胸'])
  })

  it('keeps the order unchanged for identical or invalid positions', () => {
    expect(moveItem(plans, 1, 1)).toEqual(plans)
    expect(moveItem(plans, -1, 1)).toEqual(plans)
    expect(moveItem(plans, 1, plans.length)).toEqual(plans)
  })

  it('compares the complete ordered id list', () => {
    expect(hasSameOrder(['a', 'b'], ['a', 'b'])).toBe(true)
    expect(hasSameOrder(['a', 'b'], ['b', 'a'])).toBe(false)
    expect(hasSameOrder(['a'], ['a', 'b'])).toBe(false)
  })
})
