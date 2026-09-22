// // /* BannerControl widget
// //    Usage:
// //    <div id="banner-container" data-entity="entity-slug"></div>
// //    <script src="/static/js/banner-widget.js"></script>
// // */
// // (function(){
// //   function createStyles(){
// //     const css = `
// //     .bc-banner { position: relative; width: 100%; overflow: hidden; background:#f8fafc; border-radius:8px }
// //     .bc-banner img { position:absolute; left:0; top:0; width:100%; height:100%; object-fit:cover }
// //     .bc-banner .bc-text { position:absolute; left:0; right:0; bottom:0; padding:12px 16px; background:linear-gradient(0deg, rgba(0,0,0,0.6), rgba(0,0,0,0.0)); color:white; font-size:1rem }
// //     `;
// //     const s = document.createElement('style'); s.innerHTML = css; document.head.appendChild(s);
// //   }

// //   async function fetchBanner(slug){
// //     try{
// //       const res = await fetch(`/api/banner/${encodeURIComponent(slug)}/`);
// //       return await res.json();
// //     }catch(e){ console.error('Banner fetch error', e); return null }
// //   }

// //   function mount(container){
// //     const slug = container.dataset.entity;
// //     if(!slug) return;
// //     fetchBanner(slug).then(data=>{
// //       if(!data || !data.success) return;
// //       const b = data.banner;
// //       const ratio = (b.height && b.width) ? (b.height / b.width) : 0.3;
// //       const wrapper = document.createElement('div');
// //       wrapper.className = 'bc-banner';
// //       wrapper.style.paddingTop = (ratio * 100) + '%';
// //       const img = document.createElement('img'); img.src = b.image; img.alt = b.text || slug;
// //       const text = document.createElement('div'); text.className = 'bc-text'; text.textContent = b.text || '';
// //       wrapper.appendChild(img);
// //       if(b.text) wrapper.appendChild(text);
// //       // clear container and append
// //       container.innerHTML = '';
// //       container.appendChild(wrapper);
// //       // make image resize after load to avoid flashes
// //       img.addEventListener('load', ()=>{ img.style.opacity = 1 });
// //     })
// //   }

// //   function init(){
// //     createStyles();
// //     const nodes = document.querySelectorAll('[data-entity]');
// //     nodes.forEach(el => mount(el));
// //   }

// //   if(document.readyState === 'complete' || document.readyState === 'interactive') setTimeout(init, 10);
// //   else document.addEventListener('DOMContentLoaded', init);
// // })();

// /* BannerControl Widget */
// // (function () {
// //   function createStyles() {
// //     const css = `
// //       .bc-banner {
// //         position: relative;
// //         width: 100%;
// //         overflow: hidden;
// //         background: #f8fafc;
// //         border-radius: 8px;
// //       }
// //       .bc-banner img {
// //         position: absolute;
// //         left: 0;
// //         top: 0;
// //         width: 100%;
// //         height: 100%;
// //         object-fit: cover;
// //         display: block;
// //       }
// //       .bc-banner .bc-text {
// //         position: absolute;
// //         left: 0;
// //         right: 0;
// //         bottom: 0;
// //         padding: 12px 16px;
// //         background: linear-gradient(0deg, rgba(0,0,0,0.65), transparent);
// //         color: white;
// //         font-size: 1rem;
// //         font-family: system-ui, sans-serif;
// //       }
// //     `;
// //     const style = document.createElement('style');
// //     style.innerHTML = css;
// //     document.head.appendChild(style);
// //   }

// //   async function fetchBanner(slug) {
// //     const API_BASE = 'http://127.0.0.1:8001';
// //     try {
// //       const response = await fetch(`${API_BASE}/api/banner/${encodeURIComponent(slug)}/`, {
// //         method: 'GET',
// //         headers: {
// //           'Accept': 'application/json',
// //         },
// //       });

// //       if (!response.ok) {
// //         console.error('Banner API error:', response.status, response.statusText);
// //         return null;
// //       }

// //       const json = await response.json();
// //       return json;
// //     } catch (error) {
// //       console.error('Banner fetch error:', error);
// //       return null;
// //     }
// //   }

// //   function mount(container) {
// //     const slug = container.dataset.entity;
// //     if (!slug) {
// //       console.error('Banner widget requires data-entity attribute');
// //       return;
// //     }

// //     fetchBanner(slug).then(data => {
// //       if (!data || !data.success) {
// //         console.warn('No active banner found or API error for slug:', slug);
// //         return;
// //       }

// //       const banner = data.banner;
// //       const ratio = banner.width && banner.height ? banner.height / banner.width : 0.35;

// //       const wrapper = document.createElement('div');
// //       wrapper.className = 'bc-banner';
// //       wrapper.style.paddingTop = `${ratio * 100}%`;

// //       const img = document.createElement('img');
// //       img.src = banner.image;
// //       img.alt = banner.text || slug;
// //       wrapper.appendChild(img);

// //       if (banner.text) {
// //         const textEl = document.createElement('div');
// //         textEl.className = 'bc-text';
// //         textEl.textContent = banner.text;
// //         wrapper.appendChild(textEl);
// //       }

// //       container.innerHTML = '';
// //       container.appendChild(wrapper);
// //     });
// //   }

// //   function init() {
// //     createStyles();
// //     document.querySelectorAll('[data-entity]').forEach(el => mount(el));
// //   }

// //   if (document.readyState === 'loading') {
// //     document.addEventListener('DOMContentLoaded', init);
// //   } else {
// //     init();
// //   }
// // })();

// (function () {
//   // ========== CHANGE THIS IF YOUR PORT CHANGES ==========
//   const API_BASE = "http://127.0.0.1:8001";
//   // ======================================================

//   function createStyles() {
//     const css = `
//       .bc-banner {
//         position: relative;
//         width: 100%;
//         overflow: hidden;
//         background: #f1f5f9;
//         border-radius: 8px;
//       }
//       .bc-banner img {
//         position: absolute;
//         top: 0;
//         left: 0;
//         width: 100%;
//         height: 100%;
//         object-fit: cover;
//       }
//       .bc-banner .bc-text {
//         position: absolute;
//         bottom: 0;
//         left: 0;
//         right: 0;
//         padding: 12px 16px;
//         background: linear-gradient(transparent, rgba(0,0,0,0.7));
//         color: white;
//         font-size: 1rem;
//         font-family: system-ui, sans-serif;
//       }
//     `;
//     const style = document.createElement("style");
//     style.textContent = css;
//     document.head.appendChild(style);
//   }

//   async function fetchBanner(slug) {
//     const url = `${API_BASE}/api/banner/${encodeURIComponent(slug)}/`;
//     console.log("Banner widget fetching URL:", url);

//     try {
//       const response = await fetch(url);
//       console.log("Banner widget response status:", response.status);
//       if (!response.ok) {
//         throw new Error(`HTTP error! status: ${response.status}`);
//       }
//       const json = await response.json();
//       console.log("Banner widget response JSON:", json);
//       return json;
//     } catch (error) {
//       console.error("Banner fetch error:", error);
//       return null;
//     }
//   }

//   function mount(container) {
//     const slug = container.getAttribute("data-entity");
//     if (!slug) {
//       console.error("Banner widget requires data-entity attribute");
//       return;
//     }

//     console.log("Banner widget mounting for entity:", slug);
//     fetchBanner(slug).then(data => {
//       if (!Array.isArray(data) || data.length === 0) {
//         console.warn("Banner widget got no active banners for:", slug, "data=", data);
//         return;
//       }

//       const banners = data;
//       const ratio = (banners[0].width && banners[0].height)
//         ? banners[0].height / banners[0].width
//         : 0.4;

//       const wrapper = document.createElement("div");
//       wrapper.className = "bc-banner";
//       wrapper.style.paddingTop = `${ratio * 100}%`;
//       wrapper.style.cursor = "default";

//       const img = document.createElement("img");
//       const titleDiv = document.createElement("div");
//       const textDiv = document.createElement("div");

//       titleDiv.className = "bc-title";
//       textDiv.className = "bc-text";

//       wrapper.appendChild(img);
//       wrapper.appendChild(titleDiv);
//       wrapper.appendChild(textDiv);
//       container.innerHTML = "";
//       container.appendChild(wrapper);

//       let currentIndex = 0;
//       let intervalId = null;

//       function renderSlide(index) {
//         const banner = banners[index];
//         console.log("Banner widget render slide", index, banner);

//         img.src = banner.image;
//         img.alt = banner.title || banner.text || "Banner";
//         titleDiv.textContent = banner.title || "";
//         textDiv.textContent = banner.text || "";

//         if (banner.link) {
//           wrapper.style.cursor = "pointer";
//           wrapper.onclick = () => window.open(banner.link, "_blank", "noopener");
//         } else {
//           wrapper.style.cursor = "default";
//           wrapper.onclick = null;
//         }
//       }

//       function startCarousel() {
//         if (intervalId) {
//           clearInterval(intervalId);
//         }
//         intervalId = setInterval(() => {
//           currentIndex = (currentIndex + 1) % banners.length;
//           renderSlide(currentIndex);
//         }, 5000);
//       }

//       renderSlide(currentIndex);

//       if (banners.length > 1) {
//         startCarousel();
//         container.addEventListener("mouseenter", () => {
//           if (intervalId) {
//             clearInterval(intervalId);
//             intervalId = null;
//           }
//         });
//         container.addEventListener("mouseleave", () => {
//           if (!intervalId) {
//             startCarousel();
//           }
//         });
//       }
//     });
//   }

//   function init() {
//     createStyles();
//     document.querySelectorAll("[data-entity]").forEach(mount);
//   }

//   if (document.readyState === "loading") {
//     document.addEventListener("DOMContentLoaded", init);
//   } else {
//     init();
//   }
// })();