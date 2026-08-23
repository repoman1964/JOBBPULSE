import { describe, expect, it } from 'vitest'
import { captionParts, companyInitials, instagramHandle } from '../app/utils/socialPreview'

describe('instagramHandle', () => {
  it('lowercases and strips spaces and punctuation', () => {
    expect(instagramHandle('Johnson Outdoor Living')).toBe('johnsonoutdoorliving')
  })

  it('falls back when the name is empty', () => {
    expect(instagramHandle('   ')).toBe('company')
  })
})

describe('companyInitials', () => {
  it('uses first and last words', () => {
    expect(companyInitials('Johnson Outdoor Living')).toBe('JL')
  })

  it('uses two letters of a single word', () => {
    expect(companyInitials('Acme')).toBe('AC')
  })
})

describe('captionParts', () => {
  it('splits hashtags from surrounding copy', () => {
    expect(
      captionParts('New decking in Marietta. #DeckRebuild #MariettaGA built to last.'),
    ).toEqual([
      { type: 'text', value: 'New decking in Marietta. ' },
      { type: 'tag', value: '#DeckRebuild' },
      { type: 'text', value: ' ' },
      { type: 'tag', value: '#MariettaGA' },
      { type: 'text', value: ' built to last.' },
    ])
  })

  it('returns a single text part when there are no hashtags', () => {
    expect(captionParts('Plain caption')).toEqual([{ type: 'text', value: 'Plain caption' }])
  })
})
