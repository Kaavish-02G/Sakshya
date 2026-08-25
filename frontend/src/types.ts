export type EvidenceStatus = 'Verified' | 'Processing' | 'Needs review'

export interface EvidenceFile {
  id: string
  name: string
  type: string
  size: string
  uploaded: string
  status: EvidenceStatus
  hash: string
}

export interface TimelineEvent {
  date: string
  title: string
  detail: string
  actor: string
  tone: 'teal' | 'amber' | 'slate'
}
