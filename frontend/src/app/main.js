import { config } from '../shared/config.js';
import { readLocalObject } from '../shared/lib/profile.js';
import { renderProfileCard } from '../shared/ui/ProfileCard.js';
import { createFeedPage } from '../features/feed/FeedPage.js';
import { createNoticeDetail } from '../features/notice/NoticeDetail.js';
import { createApplyPanel } from '../features/apply-helper/ApplyPanel.js';
import { prepareDemo } from '../shared/api/demo-client.js';
import { renderDemoBanner } from '../shared/ui/DemoBanner.js';

renderDemoBanner();
await prepareDemo().catch(() => {});

const applyPanel = createApplyPanel();
const noticeDetail = createNoticeDetail({
  onReady: (notice, target, signal) => {
    if (notice.ai?.status === 'done' && target) applyPanel.load(notice.id, target, signal);
  },
  onClose: applyPanel.cancel,
});
const feed = createFeedPage({
  onSelect: noticeDetail.show,
  getUserId: () => readLocalObject(config.sessionKey).userId,
});
window.addEventListener('storage', (event) => {
  if (event.key === config.profileKey || event.key === null) renderProfileCard();
  if (event.key === config.sessionKey || event.key === null) feed.refresh();
});
renderProfileCard();
