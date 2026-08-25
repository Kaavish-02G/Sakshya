import type { EvidenceFile, TimelineEvent } from './types'

export const initialEvidence: EvidenceFile[] = [
  { id: 'EV-047', name: 'Property_Deed_2019.pdf', type: 'PDF document', size: '4.2 MB', uploaded: 'Today, 10:42', status: 'Verified', hash: 'a831...4c2e' },
  { id: 'EV-046', name: 'WhatsApp_Conversation.zip', type: 'Archive', size: '18.7 MB', uploaded: 'Yesterday, 16:08', status: 'Processing', hash: 'Generating…' },
  { id: 'EV-045', name: 'Site_Inspection_Photos.jpg', type: 'Image set', size: '12.1 MB', uploaded: '21 Aug, 14:22', status: 'Needs review', hash: 'd01f...a96b' },
  { id: 'EV-044', name: 'Witness_Statement.mp3', type: 'Audio recording', size: '26.5 MB', uploaded: '20 Aug, 11:11', status: 'Verified', hash: '73bf...f04d' },
]

export const timeline: TimelineEvent[] = [
  { date: '24 AUG 2026 · 10:42', title: 'Property deed received', detail: 'Uploaded by Inspector Ananya Rao · SHA-256 fingerprint recorded.', actor: 'Police Intake', tone: 'teal' },
  { date: '23 AUG 2026 · 16:08', title: 'Chat export sent for extraction', detail: 'Transcript and metadata extraction are in progress.', actor: 'Digital Forensics Lab', tone: 'amber' },
  { date: '21 AUG 2026 · 14:22', title: 'Site inspection photographs logged', detail: 'Tamper-risk scan requires analyst review before release.', actor: 'Forensic Analyst', tone: 'amber' },
  { date: '20 AUG 2026 · 11:11', title: 'Witness statement certified', detail: 'Audio transcript and custody handoff have been verified.', actor: 'Court Registry', tone: 'slate' },
]
