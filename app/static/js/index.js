(function () {
    function $(id) { return document.getElementById(id); }
    var nav = document.querySelector('.gs-nav');

    function showModal(overlayId) {
      var el = $(overlayId);
      el.style.display = 'flex';
      document.body.style.overflow = 'hidden';
      /* hide the sticky nav so it doesn't compete with the modal */
      if (nav) nav.classList.add('gs-nav--hidden');
      /* scroll the search bar into view so the modal feels anchored */
      var searchWrap = document.querySelector('.gs-search-wrap');
      if (searchWrap) {
        searchWrap.scrollIntoView({ behavior: 'smooth', block: 'center' });
      }
      el.addEventListener('click', function (e) {
        if (e.target === el) hideModal(overlayId);
      }, { once: true });
    }
    function hideModal(overlayId) {
      $(overlayId).style.display = 'none';
      document.body.style.overflow = '';
      /* restore the nav */
      if (nav) nav.classList.remove('gs-nav--hidden');
    }

    var selectedAreaSlug = '';
    var selectedAreaName = '';
    var selectedCatSlug  = '';
    var selectedCatName  = '';

    function maybeNavigate() {
      if (selectedAreaSlug && selectedCatSlug) {
        window.location.href = '/' + selectedAreaSlug + '/' + selectedCatSlug;
      } else if (selectedAreaSlug) {
        window.location.href = '/' + selectedAreaSlug;
      }
    }

    $('btn-open-area-modal').addEventListener('click', function () {
      showModal('area-modal-overlay');
      $('area-search-input').focus();
    });
    $('close-area-modal').addEventListener('click', function () {
      hideModal('area-modal-overlay');
    });

    $('area-search-input').addEventListener('input', function () {
      var q = this.value.toLowerCase();
      var visible = 0;
      document.querySelectorAll('.gs-area-cell').forEach(function (btn) {
        var name = btn.dataset.name.toLowerCase();
        var match = name.includes(q);
        btn.style.display = match ? '' : 'none';
        if (match) visible++;
      });
      $('area-search-empty').style.display = visible === 0 && q ? 'flex' : 'none';
    });

    document.querySelectorAll('.gs-area-cell').forEach(function (btn) {
      btn.addEventListener('click', function () {
        selectedAreaSlug = this.dataset.slug;
        selectedAreaName = this.dataset.name;
        $('gs-selected-area-slug').value = selectedAreaSlug;
        $('gs-selected-area-label').textContent = selectedAreaName;
        document.querySelectorAll('.gs-area-cell').forEach(function (b) {
          b.classList.remove('selected');
        });
        this.classList.add('selected');
        hideModal('area-modal-overlay');
        maybeNavigate();
      });
    });

    $('btn-open-service-modal').addEventListener('click', function () {
      showModal('service-modal-overlay');
      $('service-search-input').focus();
    });
    $('close-service-modal').addEventListener('click', function () {
      hideModal('service-modal-overlay');
    });

    $('service-search-input').addEventListener('input', function () {
      var q = this.value.toLowerCase();
      var visible = 0;
      document.querySelectorAll('.gs-service-row').forEach(function (row) {
        var name = row.dataset.name.toLowerCase();
        var subs = row.querySelector('.gs-service-row-subs').textContent.toLowerCase();
        var match = name.includes(q) || subs.includes(q);
        row.style.display = match ? '' : 'none';
        if (match) visible++;
      });
      $('service-search-empty').style.display = visible === 0 && q ? 'flex' : 'none';
    });

    document.querySelectorAll('.gs-service-row').forEach(function (row) {
      row.addEventListener('click', function () {
        selectedCatSlug = this.dataset.slug;
        selectedCatName = this.dataset.name;
        $('gs-selected-service-slug').value = selectedCatSlug;
        $('gs-selected-service-label').textContent = selectedCatName;
        hideModal('service-modal-overlay');
        maybeNavigate();
      });
    });

    document.addEventListener('keydown', function (e) {
      if (e.key === 'Escape') {
        hideModal('area-modal-overlay');
        hideModal('service-modal-overlay');
      }
    });

    /* ── FAQ ACCORDION ── */
    (function () {
      var items = document.querySelectorAll('.gs-faq-q');
      items.forEach(function (btn) {
        btn.addEventListener('click', function () {
          var isOpen = this.getAttribute('aria-expanded') === 'true';
          /* close all */
          items.forEach(function (b) {
            b.setAttribute('aria-expanded', 'false');
            var ans = b.nextElementSibling;
            if (ans) ans.hidden = true;
          });
          /* open clicked one if it was closed */
          if (!isOpen) {
            this.setAttribute('aria-expanded', 'true');
            var answer = this.nextElementSibling;
            if (answer) answer.hidden = false;
          }
        });
      });
    })();
  })();

/* ── POPULAR SERVICES TICKER ─────────────────────── */
(function () {
  const slides = document.querySelectorAll('.gs-popular-slide');
  const dots   = document.querySelectorAll('.gs-popular-dot');
  const bgs    = document.querySelectorAll('.gs-popular-bg');
  if (!slides.length) return;

  let current = 0;

  function goTo(n) {
    slides[current].classList.remove('gs-popular-slide--active');
    dots[current].classList.remove('gs-popular-dot--active');
    if (bgs[current]) bgs[current].classList.remove('gs-popular-bg--active');
    current = (n + slides.length) % slides.length;
    slides[current].classList.add('gs-popular-slide--active');
    dots[current].classList.add('gs-popular-dot--active');
    if (bgs[current]) bgs[current].classList.add('gs-popular-bg--active');
  }

  setInterval(() => goTo(current + 1), 3200);
}());