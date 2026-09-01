// /**
//  * Multi-Entity Banner & Events Widget
//  * Embeddable widget script to display banners and upcoming events for an entity.
//  * 
//  * Usage:
//  * <div id="banner-widget-container" data-slug="tech-corp" data-api-base="http://127.0.0.1:8001"></div>
//  * <script src="http://127.0.0.1:8001/static/js/banner-widget.js"></script>
//  */

// (function () {
//     'use strict';

//     const DEFAULT_API_BASE = 'http://127.0.0.1:8001';
//     const PLACEHOLDER_IMAGE = 'data:image/svg+xml;utf8,<svg xmlns="http://www.w3.org/2000/svg" width="800" height="300" viewBox="0 0 800 300"><rect width="800" height="300" fill="%232c3e50"/><text x="50%" y="50%" dominant-baseline="middle" text-anchor="middle" fill="%23ecf0f1" font-family="sans-serif" font-size="28">Upcoming Event</text></svg>';

//     async function initWidget() {
//         const container = document.getElementById('banner-widget-container');
//         if (!container) return;

//         const slug = container.getAttribute('data-slug') || 'tech-corp';
//         const apiBase = container.getAttribute('data-api-base') || DEFAULT_API_BASE;

//         // Fetch Banners and Events from APIs
//         try {
//             const [bannersRes, eventsRes] = await Promise.all([
//                 fetch(`${apiBase}/api/banner/${slug}/`).then(r => r.json()).catch(() => null),
//                 fetch(`${apiBase}/api/events/${slug}/`).then(r => r.json()).catch(() => null)
//             ]);

//             renderWidget(container, bannersRes, eventsRes);
//         } catch (error) {
//             console.error('Error initializing Banner Widget:', error);
//             container.innerHTML = '<div style="color: red; padding: 1rem;">Failed to load widget content.</div>';
//         }
//     }

//     function renderWidget(container, bannersData, eventsData) {
//         const entityName = (bannersData && bannersData.entity) || (eventsData && eventsData.entity) || 'Entity';
//         const banners = (bannersData && bannersData.banners) || [];
//         const events = (eventsData && eventsData.upcoming_events) || [];

//         let html = `
//             <style>
//                 .bw-widget-wrapper {
//                     font-family: system-ui, -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif;
//                     max-width: 900px;
//                     margin: 0 auto;
//                     padding: 16px;
//                     background: #f8f9fa;
//                     border-radius: 12px;
//                     box-shadow: 0 4px 12px rgba(0,0,0,0.08);
//                 }
//                 .bw-header {
//                     font-size: 1.5rem;
//                     font-weight: 700;
//                     color: #1a252f;
//                     margin-bottom: 20px;
//                     border-bottom: 2px solid #e2e8f0;
//                     padding-bottom: 8px;
//                 }
//                 .bw-section-title {
//                     font-size: 1.2rem;
//                     font-weight: 600;
//                     color: #2d3748;
//                     margin: 24px 0 12px 0;
//                 }
//                 .bw-banners-grid {
//                     display: grid;
//                     grid-template-columns: repeat(auto-fit, minmax(280px, 1fr));
//                     gap: 16px;
//                 }
//                 .bw-banner-card {
//                     background: #fff;
//                     border-radius: 8px;
//                     overflow: hidden;
//                     border: 1px solid #e2e8f0;
//                     transition: transform 0.2s ease, box-shadow 0.2s ease;
//                 }
//                 .bw-banner-card:hover {
//                     transform: translateY(-2px);
//                     box-shadow: 0 6px 16px rgba(0,0,0,0.12);
//                 }
//                 .bw-banner-img {
//                     width: 100%;
//                     height: 160px;
//                     object-fit: cover;
//                     display: block;
//                 }
//                 .bw-card-body {
//                     padding: 14px;
//                 }
//                 .bw-card-title {
//                     font-weight: 600;
//                     font-size: 1.05rem;
//                     color: #1a202c;
//                     margin-bottom: 6px;
//                 }
//                 .bw-card-text {
//                     font-size: 0.9rem;
//                     color: #4a5568;
//                     line-height: 1.4;
//                     margin-bottom: 10px;
//                 }
//                 .bw-events-grid {
//                     display: grid;
//                     grid-template-columns: repeat(auto-fit, minmax(280px, 1fr));
//                     gap: 16px;
//                 }
//                 .bw-event-card {
//                     background: #ffffff;
//                     border-radius: 8px;
//                     overflow: hidden;
//                     border: 1px solid #e2e8f0;
//                     box-shadow: 0 2px 8px rgba(0,0,0,0.06);
//                     display: flex;
//                     flex-direction: column;
//                 }
//                 .bw-event-banner {
//                     width: 100%;
//                     height: 160px;
//                     object-fit: cover;
//                     display: block;
//                     background-color: #edf2f7;
//                 }
//                 .bw-event-date-badge {
//                     display: inline-block;
//                     background: #ebf8ff;
//                     color: #2b6cb0;
//                     font-weight: 600;
//                     font-size: 0.8rem;
//                     padding: 4px 8px;
//                     border-radius: 4px;
//                     margin-bottom: 8px;
//                 }
//             </style>
//             <div class="bw-widget-wrapper">
//                 <div class="bw-header">${entityName} - Banners & Upcoming Events</div>
//         `;

//         // Render Banners Section
//         if (banners.length > 0) {
//             html += `
//                 <div class="bw-section-title">Promotional Banners</div>
//                 <div class="bw-banners-grid">
//             `;
//             banners.forEach(b => {
//                 const imgUrl = b.image || PLACEHOLDER_IMAGE;
//                 html += `
//                     <div class="bw-banner-card">
//                         <img src="${imgUrl}" alt="${b.title}" class="bw-banner-img" />
//                         <div class="bw-card-body">
//                             <div class="bw-card-title">${b.title}</div>
//                             <div class="bw-card-text">${b.text}</div>
//                         </div>
//                     </div>
//                 `;
//             });
//             html += `</div>`;
//         }

//         // Render Upcoming Events Section
//         if (events.length > 0) {
//             html += `
//                 <div class="bw-section-title">Upcoming Events</div>
//                 <div class="bw-events-grid">
//             `;
//             events.forEach(e => {
//                 // Event image banner with fallback
//                 const eventImg = e.image || PLACEHOLDER_IMAGE;
//                 html += `
//                     <div class="bw-event-card">
//                         <img src="${eventImg}" alt="${e.name}" class="bw-event-banner" onError="this.src='${PLACEHOLDER_IMAGE}';" />
//                         <div class="bw-card-body">
//                             <div class="bw-event-date-badge">📅 ${e.event_date || 'TBD'}</div>
//                             <div class="bw-card-title">${e.name}</div>
//                             <div class="bw-card-text">${e.description}</div>
//                         </div>
//                     </div>
//                 `;
//             });
//             html += `</div>`;
//         }

//         html += `</div>`;
//         container.innerHTML = html;
//     }

//     if (document.readyState === 'loading') {
//         document.addEventListener('DOMContentLoaded', initWidget);
//     } else {
//         initWidget();
//     }
// })();
