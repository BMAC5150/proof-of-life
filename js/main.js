(function () {
  'use strict'

  // --- Landing page: CONTENTS dropdown ---
  var contentsBtn = document.querySelector('.contents-btn')
  var contentsDropdown = document.querySelector('.contents-dropdown')

  if (contentsBtn && contentsDropdown) {
    function openDropdown() {
      contentsDropdown.classList.add('is-open')
      contentsDropdown.setAttribute('aria-hidden', 'false')
      contentsBtn.setAttribute('aria-expanded', 'true')
    }
    function closeDropdown() {
      contentsDropdown.classList.remove('is-open')
      contentsDropdown.setAttribute('aria-hidden', 'true')
      contentsBtn.setAttribute('aria-expanded', 'false')
    }
    contentsBtn.addEventListener('click', function () {
      contentsDropdown.classList.contains('is-open') ? closeDropdown() : openDropdown()
    })
    document.addEventListener('click', function (e) {
      if (!contentsBtn.contains(e.target) && !contentsDropdown.contains(e.target)) {
        closeDropdown()
      }
    })
    document.addEventListener('keydown', function (e) {
      if (e.key === 'Escape') closeDropdown()
    })
    contentsDropdown.querySelectorAll('a').forEach(function (link) {
      link.addEventListener('click', closeDropdown)
    })
  }

  // --- Chapter/overview pages: nav drawer ---
  var toggle = document.querySelector('.nav-toggle')
  var closeBtn = document.querySelector('.nav-close')
  var drawer = document.querySelector('.nav-drawer')
  var overlay = document.querySelector('.nav-overlay')

  if (!toggle || !drawer) return

  function openDrawer() {
    drawer.classList.add('is-open')
    if (overlay) overlay.classList.add('is-visible')
    toggle.setAttribute('aria-expanded', 'true')
    drawer.setAttribute('aria-hidden', 'false')
    document.body.style.overflow = 'hidden'
    if (closeBtn) closeBtn.focus()
  }
  function closeDrawer() {
    drawer.classList.remove('is-open')
    if (overlay) overlay.classList.remove('is-visible')
    toggle.setAttribute('aria-expanded', 'false')
    drawer.setAttribute('aria-hidden', 'true')
    document.body.style.overflow = ''
    toggle.focus()
  }

  toggle.addEventListener('click', openDrawer)
  if (closeBtn) closeBtn.addEventListener('click', closeDrawer)
  if (overlay) overlay.addEventListener('click', closeDrawer)
  document.addEventListener('keydown', function (e) {
    if (e.key === 'Escape' && drawer.classList.contains('is-open')) closeDrawer()
  })
  drawer.querySelectorAll('a').forEach(function (link) {
    link.addEventListener('click', closeDrawer)
  })
})()
