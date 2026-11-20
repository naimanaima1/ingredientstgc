/* Visitor analytics for library.thegoodcoil.com: Google Analytics 4 + PostHog.
   Use the SAME two IDs as thegoodcoil.com and itsjara.com, so one visitor can be followed
   across all three sites. Both IDs are public by design. Leave one empty to switch that tool off.
   tgcTrack('event_name', { ... }) sends a custom event to both; never pass emails or names. */
(function () {
  var GA_MEASUREMENT_ID = 'G-756WSDMEC1';
  var POSTHOG_KEY = 'phc_na6bWvbXVNWcA8iJvhXg4WSqcVMdc9eTkmmdW95QafrK';
  var POSTHOG_HOST = 'https://us.i.posthog.com';   // EU projects: 'https://eu.i.posthog.com'

  window.tgcTrack = function () {};
  var h = location.hostname;
  if (h === 'localhost' || h === '127.0.0.1' || location.protocol === 'file:') return;
  if (/(^|\/)[a-z0-9-]*-test(\/|$)|\/test-/.test(location.pathname)) return; // test pages stay out

  if (GA_MEASUREMENT_ID) {
    var s = document.createElement('script');
    s.async = true;
    s.src = 'https://www.googletagmanager.com/gtag/js?id=' + GA_MEASUREMENT_ID;
    document.head.appendChild(s);
    window.dataLayer = window.dataLayer || [];
    window.gtag = function () { dataLayer.push(arguments); };
    gtag('js', new Date());
    gtag('config', GA_MEASUREMENT_ID);
  }

  if (POSTHOG_KEY) {
    // PostHog's standard loader snippet.
    !function(t,e){var o,n,p,r;e.__SV||(window.posthog=e,e._i=[],e.init=function(i,s,a){function g(t,e){var o=e.split(".");2==o.length&&(t=t[o[0]],e=o[1]),t[e]=function(){t.push([e].concat(Array.prototype.slice.call(arguments,0)))}}(p=t.createElement("script")).type="text/javascript",p.crossOrigin="anonymous",p.async=!0,p.src=s.api_host.replace(".i.posthog.com","-assets.i.posthog.com")+"/static/array.js",(r=t.getElementsByTagName("script")[0]).parentNode.insertBefore(p,r);var u=e;for(void 0!==a?u=e[a]=[]:a="posthog",u.people=u.people||[],u.toString=function(t){var e="posthog";return"posthog"!==a&&(e+="."+a),t||(e+=" (stub)"),e},u.people.toString=function(){return u.toString(1)+".people (stub)"},o="init capture register register_once register_for_session unregister unregister_for_session getFeatureFlag getFeatureFlagPayload isFeatureEnabled reloadFeatureFlags updateEarlyAccessFeatureEnrollment getEarlyAccessFeatures on onFeatureFlags onSessionId getSurveys getActiveMatchingSurveys renderSurvey canRenderSurvey getNextSurveyStep identify setPersonProperties group resetGroups setPersonPropertiesForFlags resetPersonPropertiesForFlags setGroupPropertiesForFlags resetGroupPropertiesForFlags reset get_distinct_id getGroups get_session_id get_session_replay_url alias set_config startSessionRecording stopSessionRecording sessionRecordingStarted captureException loadToolbar get_property getSessionProperty createPersonProfile opt_in_capturing opt_out_capturing has_opted_in_capturing has_opted_out_capturing clear_opt_in_out_capturing debug".split(" "),n=0;n<o.length;n++)g(u,o[n]);e._i.push([i,s,a])},e.__SV=1)}(document,window.posthog||[]);
    posthog.init(POSTHOG_KEY, {
      api_host: POSTHOG_HOST,
      defaults: '2025-05-24',
      person_profiles: 'identified_only',
      cross_subdomain_cookie: true, // shares the visitor id with thegoodcoil.com
      session_recording: { maskAllInputs: false, maskInputOptions: { email: true, password: true } }
    });
  }

  // Links to JARA carry this visitor's PostHog ids (ph_did, ph_sid), so itsjara.com counts the
  // same person instead of a new one. Added at click time, so the ids are always current.
  document.addEventListener('click', function (ev) {
    var a = ev.target && ev.target.closest ? ev.target.closest('a[href*="itsjara.com"]') : null;
    if (!a || !window.posthog || !posthog.get_distinct_id) return;
    try {
      var u = new URL(a.href);
      u.searchParams.set('ph_did', posthog.get_distinct_id());
      var sid = posthog.get_session_id && posthog.get_session_id();
      if (sid) u.searchParams.set('ph_sid', sid);
      a.href = u.toString();
    } catch (e) { /* leave the link as it was */ }
  }, true);

  window.tgcTrack = function (name, props) {
    try {
      if (window.gtag) gtag('event', name, props || {});
      if (window.posthog && posthog.capture) posthog.capture(name, props || {});
    } catch (e) { /* never break the page */ }
  };
})();
