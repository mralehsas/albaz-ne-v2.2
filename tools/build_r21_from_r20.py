from pathlib import Path
p=Path('engine/hilal_unified_map5_engine.cc')
s=p.read_text(encoding='utf-8')

def one(old,new,label):
    global s
    if old not in s:
        raise SystemExit(f'missing patch anchor: {label}')
    s=s.replace(old,new,1)

one('static constexpr const char *HILAL_ENGINE_SIGNATURE = "ALBAZ_UNIFIED_MAP5_ENGINE_R20_HD";',
    'static constexpr const char *HILAL_ENGINE_SIGNATURE = "ALBAZ_MAP_ENGINE_R21_REBUILD";','signature')
one('static constexpr const char *HILAL_ENGINE_BUILD = "unified-map5-r20-hd-2026-09-09";',
    'static constexpr const char *HILAL_ENGINE_BUILD = "map-engine-r21-rebuild-2026-09-09";','build')
one('// R20 IQ200 UNIFIED MAP5 SCIENTIFIC-HD FAST PATH\n// One OpenMP world-grid pass produces Odeh + Yallop + Allawi + SAAO +\n// ALBAZ-NE V2.2/S01. Common sunset/moonset and lunar-phase searches are shared.\n// The legacy map/map4/map3 commands below are intentionally preserved as an\n// immutable reference/validation lane; production should call map5.',
'''// R21 IQ200 MAP ENGINE REBUILD — SCIENTIFIC CONTRACT
// One OpenMP world-grid pass produces Odeh + Yallop + Allawi + SAAO +
// ALBAZ-NE V2.2/S01. Civil date -> local sunset -> local geometry -> criterion.
// R21 intentionally writes criterion categories only; grids/isochrones/smoothing
// are presentation layers and cannot overwrite scientific pixels.''','header')
one('static constexpr const char *MAP5_SIGNATURE = "HILAL_UNIFIED_MAP5_R20_HD";',
    'static constexpr const char *MAP5_SIGNATURE = "HILAL_MAP_ENGINE_R21_REBUILD";','map sig')
start=s.index('static astro_search_result_t search_previous_moon_phase_forward')
end=s.index('\nstruct PhaseBracket',start)
phase='''static PhaseWindow build_phase_window(astro_time_t base) {
    // R21: build an ordered conjunction sequence by walking FORWARD from a
    // date safely before the requested civil day. Never infer "previous new
    // moon" from the first event in a long forward window.
    PhaseWindow w;
    astro_time_t cursor = Astronomy_AddDays(base, -36.0);
    std::array<astro_time_t, 4> seq{};
    for (int i=0; i<4; ++i) {
        astro_search_result_t r = Astronomy_SearchMoonPhase(0.0, cursor, +40.0);
        if (r.status != ASTRO_SUCCESS) return w;
        seq[(size_t)i] = r.time;
        cursor = Astronomy_AddDays(r.time, +0.05);
    }
    for (size_t i=1; i<seq.size(); ++i) {
        if (!(seq[i].ut > seq[i-1].ut)) return w;
    }
    w.p = seq;
    w.ok = true;
    return w;
}
'''
s=s[:start]+phase+s[end:]
old='''    if (!std::isfinite(prev_ut) || !std::isfinite(next_ut)) {
        // Exact safety fallback; should never trigger for a normal civil-date map.
        astro_search_result_t ps = search_previous_moon_phase_forward(0.0, t, 35.0);
        astro_search_result_t ns = Astronomy_SearchMoonPhase(0.0, t, +35.0);
        if (ps.status != ASTRO_SUCCESS || ns.status != ASTRO_SUCCESS) return b;
        b.prev = ps.time; b.next = ns.time;
    }
'''
new='''    if (!std::isfinite(prev_ut) || !std::isfinite(next_ut)) {
        // Exact safety fallback; should never trigger for a normal civil-date map.
        astro_time_t cursor = Astronomy_AddDays(t, -36.0);
        astro_search_result_t r1 = Astronomy_SearchMoonPhase(0.0, cursor, +40.0);
        if (r1.status != ASTRO_SUCCESS) return b;
        astro_search_result_t r2 = Astronomy_SearchMoonPhase(0.0, Astronomy_AddDays(r1.time, +0.05), +40.0);
        if (r2.status != ASTRO_SUCCESS) return b;
        astro_search_result_t r3 = Astronomy_SearchMoonPhase(0.0, Astronomy_AddDays(r2.time, +0.05), +40.0);
        if (r3.status != ASTRO_SUCCESS) return b;
        std::array<astro_time_t,3> local = {r1.time,r2.time,r3.time};
        for (const auto& p : local) {
            if (p.ut <= t.ut && p.ut > prev_ut) { b.prev=p; prev_ut=p.ut; }
            if (p.ut >= t.ut && p.ut < next_ut) { b.next=p; next_ut=p.ut; }
        }
        if (!std::isfinite(prev_ut) || !std::isfinite(next_ut)) return b;
    }
'''
one(old,new,'phase fallback')
cs=s.index('static inline uint32_t color_odeh_yallop')
ce=s.index('static inline uint32_t color_allawi',cs)
colors='''static inline uint32_t color_odeh(char code) {
    if      (code == 'A') return 0xFF50B000;
    else if (code == 'B') return 0xFFFF4DFF;
    else if (code == 'C') return 0xFFFF5B2F;
    else if (code == 'D') return 0x00000000;
    else if (code == 'G' || code == 'I' || code == 'J') return 0xFF2B2BFF;
    else if (code == 'H') return 0xFFE6E040;
    return 0x00000000;
}

static inline uint32_t color_yallop(char code) {
    if      (code == 'A') return 0xFF50B000;
    else if (code == 'B') return 0xFF4DD3FF;
    else if (code == 'C') return 0xFFFF4DFF;
    else if (code == 'D') return 0xFFFF5B2F;
    else if (code == 'E' || code == 'F') return 0x00000000;
    else if (code == 'G' || code == 'I' || code == 'J') return 0xFF2B2BFF;
    else if (code == 'H') return 0xFFE6E040;
    return 0x00000000;
}

'''
s=s[:cs]+colors+s[ce:]
ss=s.index('static inline uint32_t color_saao')
se=s.index('static inline uint32_t color_albaz_v22',ss)
saao='''static inline uint32_t color_saao(char code) {
    if      (code == 'A') return 0xFF50B000;
    else if (code == 'C') return 0xFFFF5B2F;
    else if (code == 'F') return 0x00000000;
    else if (code == 'G' || code == 'I' || code == 'J') return 0xFF2B2BFF;
    else if (code == 'H') return 0xFFE6E040;
    return 0x00000000;
}

'''
s=s[:ss]+saao+s[se:]
anchor='struct Map5Cell {'
helper='''static int surface_conjunction_state(astro_observer_t observer, astro_time_t t) {
    const astro_equatorial_t sun_eq = Astronomy_Equator(BODY_SUN, &t, observer, EQUATOR_OF_DATE, ABERRATION);
    const astro_equatorial_t moon_eq = Astronomy_Equator(BODY_MOON, &t, observer, EQUATOR_OF_DATE, ABERRATION);
    if (sun_eq.status != ASTRO_SUCCESS || moon_eq.status != ASTRO_SUCCESS) return 0;
    const double slon = topocentric_ecliptic_lon(t, sun_eq);
    const double mlon = topocentric_ecliptic_lon(t, moon_eq);
    if (!std::isfinite(slon) || !std::isfinite(mlon)) return 0;
    return (normalize_angle_deg(mlon - slon) >= 0.0) ? +1 : -1;
}

'''
one(anchor,helper+anchor,'surface helper')
one('            const bool before_new_moon = (sunset.time.ut - pb.nearest.ut) < 0.0;\n            astro_time_t best_time =',
    '            const int surface_state = surface_conjunction_state(observer, sunset.time);\n            const bool before_new_moon = (surface_state < 0);\n            astro_time_t best_time =','surface state')
one("            if (lag < 0.0 && before_new_moon) { out.odeh='J'; out.yallop='J'; }",
    "            if (surface_state == 0) { out.odeh='H'; out.yallop='H'; }\n            else if (lag < 0.0 && before_new_moon) { out.odeh='J'; out.yallop='J'; }",'special refs')
one("out.odeh = (v_odeh >= 5.65) ? 'A' : (v_odeh >= 2.00 ? 'C' : (v_odeh >= -.96 ? 'E' : 'F'));",
    "out.odeh = (v_odeh >= 5.65) ? 'A' : (v_odeh >= 2.00 ? 'B' : (v_odeh >= -.96 ? 'C' : 'D'));",'odeh codes')
one('if (lag <= 0.0 || age_hours <= 0.0) {','if (lag <= 0.0 || surface_state <= 0 || age_hours <= 0.0) {','allawi special')
one("            if (lag < 0.0 && before_new_moon) out.saao='J';",
    "            if (surface_state == 0) out.saao='H';\n            else if (lag < 0.0 && before_new_moon) out.saao='J';",'saao special')
s=s.replace('        if (!impossible && apb.next.ut >= st.ut && (apb.next.ut - st.ut) <= 3.0) impossible = true; // central conjunction after sunset within authority search window\n','',1)
one('// R20 scientific raster contract: CATEGORY PIXELS ONLY.','// R21 scientific raster contract: CATEGORY PIXELS ONLY.','raster comment')
one('    o=color_odeh_yallop(r.odeh);\n    y=color_odeh_yallop(r.yallop);','    o=color_odeh(r.odeh);\n    y=color_yallop(r.yallop);','store colors')
anchor='static bool parse_date(const char *text, int &year, int &month, int &day) {'
phase_debug='''static int cmd_phase_debug(astro_time_t base_time) {
    const PhaseWindow w = build_phase_window(base_time);
    if (!w.ok) { std::fprintf(stderr, "PHASE_WINDOW=FAIL\\n"); return 4; }
    std::printf("PHASE_WINDOW=PASS\\n");
    for (size_t i=0; i<w.p.size(); ++i) {
        char text[TIME_TEXT_BYTES];
        astro_status_t st = Astronomy_FormatTime(w.p[i], TIME_FORMAT_SECOND, text, sizeof(text));
        if (st != ASTRO_SUCCESS) std::snprintf(text, sizeof(text), "UT=%.9f", w.p[i].ut);
        std::printf("NEW_MOON_%zu=%s UT=%.9f\\n", i, text, w.p[i].ut);
    }
    const astro_time_t probe = Astronomy_AddDays(base_time, 0.75);
    const PhaseBracket b = phase_bracket(w, probe);
    if (!b.ok) return 4;
    char prev[TIME_TEXT_BYTES], next[TIME_TEXT_BYTES];
    Astronomy_FormatTime(b.prev, TIME_FORMAT_SECOND, prev, sizeof(prev));
    Astronomy_FormatTime(b.next, TIME_FORMAT_SECOND, next, sizeof(next));
    std::printf("PROBE_PREV=%s\\nPROBE_NEXT=%s\\n", prev, next);
    return 0;
}

'''
one(anchor,phase_debug+anchor,'phase debug')
one('        fprintf(stderr, "Usage: <date> map5 evening <odeh.png> <yallop.png> <allawi.png> <saao.png> <albaz.png>\\n");',
    '        fprintf(stderr, "Usage: <date> phase-debug | <date> map5 evening <odeh.png> <yallop.png> <allawi.png> <saao.png> <albaz.png>\\n");','usage')
one('    astro_time_t time = Astronomy_MakeTime(year, month, day, 0, 0, 0);\n\n    if (!strcmp(argv[2], "map5")) {',
    '    astro_time_t time = Astronomy_MakeTime(year, month, day, 0, 0, 0);\n\n    if (!strcmp(argv[2], "phase-debug")) {\n        return cmd_phase_debug(time);\n    }\n\n    if (!strcmp(argv[2], "map5")) {','phase route')
one('Invalid command. Production R20 supports MAP5 only.','Invalid command. Production R21 supports MAP5 only.','invalid')
p.write_text(s,encoding='utf-8')
