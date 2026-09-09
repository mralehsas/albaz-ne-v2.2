from pathlib import Path
p=Path('engine/hilal_unified_map5_engine.cc')
s=p.read_text(encoding='utf-8')

def one(old,new,label):
    global s
    if old not in s:
        raise SystemExit(f'missing anchor: {label}')
    s=s.replace(old,new,1)

one('static constexpr const char *HILAL_ENGINE_SIGNATURE = "ALBAZ_MAP_ENGINE_R21_REBUILD";',
    'static constexpr const char *HILAL_ENGINE_SIGNATURE = "ALBAZ_MAP_ENGINE_R22_SMART";','signature')
one('static constexpr const char *HILAL_ENGINE_BUILD = "map-engine-r21-rebuild-2026-09-09";',
    'static constexpr const char *HILAL_ENGINE_BUILD = "map-engine-r22-smart-2026-09-09";','build')
one('static constexpr const char *MAP5_SIGNATURE = "HILAL_MAP_ENGINE_R21_REBUILD";',
    'static constexpr const char *MAP5_SIGNATURE = "HILAL_MAP_ENGINE_R22_SMART";','map signature')
one('// R21 IQ200 MAP ENGINE REBUILD — SCIENTIFIC CONTRACT',
    '// R22 SMART MAP ENGINE — R21 SCIENCE FROZEN + ADAPTIVE DISPLAY','header')
one('// R21 intentionally writes criterion categories only; grids/isochrones/smoothing\n// are presentation layers and cannot overwrite scientific pixels.',
    '// R22 keeps the R21 scientific category raster immutable. Smart preview adds exact\n// half-degree recomputation only near class boundaries; it never interpolates classes.','contract')
one('// R21 scientific raster contract: CATEGORY PIXELS ONLY.',
    '// R22 scientific raster contract: CATEGORY PIXELS ONLY.','raster contract')

anchor='''static int cmd_albaz_eval_v22(const char* w_text, const char* arcv_text) {'''
smart=r'''

static inline bool map5_cell_differs(const Map5Cell& a, const Map5Cell& b) {
    return a.odeh != b.odeh || a.yallop != b.yallop || a.allawi != b.allawi || a.saao != b.saao || a.albaz != b.albaz;
}

static int render_map5_smart_evening(astro_time_t base_time, const char* odeh_png, const char* yallop_png,
                                     const char* allawi_png, const char* saao_png, const char* albaz_png) {
    // SMART PREVIEW CONTRACT
    // 1) exact base world classification at the native PPD=1 grid;
    // 2) detect all multi-criterion categorical boundaries;
    // 3) one-cell safety dilation;
    // 4) exact 0.5-degree recomputation only in those boundary neighborhoods;
    // 5) outside boundaries, nearest categorical replication only (never color interpolation).
    const PhaseWindow phases = build_phase_window(base_time);
    if (!phases.ok) return 4;

    if (pixelsPerDegree >= 2) {
        return render_map5_evening(base_time, odeh_png, yallop_png, allawi_png, saao_png, albaz_png);
    }

    const unsigned base_w = width;
    const unsigned base_h = height;
    const size_t base_n = (size_t)base_w * base_h;
    std::vector<Map5Cell> base(base_n);

#if defined(_OPENMP)
    #pragma omp parallel for schedule(static)
#endif
    for (int ix=0; ix<(int)base_w; ++ix) {
        for (unsigned iy=0; iy<base_h; ++iy) {
            const double lat=((base_h-(iy+1))/(double)pixelsPerDegree)+minLatitude;
            const double lon=(ix/(double)pixelsPerDegree)+minLongitude;
            base[(size_t)ix+(size_t)iy*base_w] = evaluate_map5_cell_evening(lat,lon,base_time,phases);
        }
    }

    std::vector<uint8_t> boundary(base_n, 0), refine(base_n, 0);
    for (unsigned iy=0; iy<base_h; ++iy) {
        for (unsigned ix=0; ix<base_w; ++ix) {
            const Map5Cell& c = base[(size_t)ix+(size_t)iy*base_w];
            bool diff = false;
            for (int dy=-1; dy<=1 && !diff; ++dy) {
                const int ny=(int)iy+dy;
                if (ny<0 || ny>=(int)base_h) continue;
                for (int dx=-1; dx<=1; ++dx) {
                    if (!dx && !dy) continue;
                    int nx=(int)ix+dx;
                    if (nx < 0) nx += (int)base_w;
                    if (nx >= (int)base_w) nx -= (int)base_w;
                    if (map5_cell_differs(c, base[(size_t)nx+(size_t)ny*base_w])) { diff=true; break; }
                }
            }
            if (diff) boundary[(size_t)ix+(size_t)iy*base_w]=1;
        }
    }

    refine = boundary;
    std::vector<uint8_t> next = refine;
    for (unsigned iy=0; iy<base_h; ++iy) {
        for (unsigned ix=0; ix<base_w; ++ix) {
            if (!refine[(size_t)ix+(size_t)iy*base_w]) continue;
            for (int dy=-1; dy<=1; ++dy) {
                const int ny=(int)iy+dy;
                if (ny<0 || ny>=(int)base_h) continue;
                for (int dx=-1; dx<=1; ++dx) {
                    int nx=(int)ix+dx;
                    if (nx<0) nx+=(int)base_w;
                    if (nx>=(int)base_w) nx-=(int)base_w;
                    next[(size_t)nx+(size_t)ny*base_w]=1;
                }
            }
        }
    }
    refine.swap(next);

    const unsigned target_ppd = 2;
    const unsigned target_w = (maxLongitude-minLongitude)*target_ppd;
    const unsigned target_h = (maxLatitude-minLatitude)*target_ppd;
    const size_t target_n = (size_t)target_w*target_h;
    std::vector<uint32_t> o(target_n), y(target_n), a(target_n), ss(target_n), b(target_n);

    size_t refine_cells=0;
    for (uint8_t v: refine) refine_cells += (v ? 1u : 0u);

#if defined(_OPENMP)
    #pragma omp parallel for schedule(static)
#endif
    for (int tx=0; tx<(int)target_w; ++tx) {
        for (unsigned ty=0; ty<target_h; ++ty) {
            const unsigned bx = std::min(base_w-1, (unsigned)((uint64_t)tx * base_w / target_w));
            const unsigned by = std::min(base_h-1, (unsigned)((uint64_t)ty * base_h / target_h));
            Map5Cell r;
            if (refine[(size_t)bx+(size_t)by*base_w]) {
                const double lat=((target_h-(ty+1))/(double)target_ppd)+minLatitude;
                const double lon=(tx/(double)target_ppd)+minLongitude;
                r = evaluate_map5_cell_evening(lat,lon,base_time,phases);
            } else {
                r = base[(size_t)bx+(size_t)by*base_w];
            }
            const size_t k=(size_t)tx+(size_t)ty*target_w;
            map5_store_colors(r,o[k],y[k],a[k],ss[k],b[k]);
        }
    }

    std::fprintf(stdout,
        "SMART_BASE_CELLS=%zu SMART_REFINED_BASE_CELLS=%zu SMART_REFINED_FRACTION=%.6f SMART_OUTPUT_PPD=%u\n",
        base_n, refine_cells, base_n ? (double)refine_cells/(double)base_n : 0.0, target_ppd);
    int ok=1;
    ok &= stbi_write_png(odeh_png,target_w,target_h,4,o.data(),target_w*4);
    ok &= stbi_write_png(yallop_png,target_w,target_h,4,y.data(),target_w*4);
    ok &= stbi_write_png(allawi_png,target_w,target_h,4,a.data(),target_w*4);
    ok &= stbi_write_png(saao_png,target_w,target_h,4,ss.data(),target_w*4);
    ok &= stbi_write_png(albaz_png,target_w,target_h,4,b.data(),target_w*4);
    return ok ? 0 : 3;
}

'''
if anchor not in s:
    raise SystemExit('missing smart insert anchor')
s=s.replace(anchor,smart+anchor,1)

one('printf("render=clean-categorical-full-grid\\ncalc_step_deg=%.8g\\nboundary_step_deg=%.8g\\noutput_ppd=%u\\n", 1.0/pixelsPerDegree, 1.0/pixelsPerDegree, pixelsPerDegree);',
    'printf("render=clean-categorical-full-grid\\ncalc_step_deg=%.8g\\nboundary_step_deg=%.8g\\noutput_ppd=%u\\n", 1.0/pixelsPerDegree, 1.0/pixelsPerDegree, pixelsPerDegree);\n        printf("smart_adaptive=1\\nsmart_output_ppd=2\\nsmart_boundary_dilation_deg=1\\n");',
    'version smart')
one('fprintf(stderr, "Usage: <date> phase-debug | <date> map5 evening <odeh.png> <yallop.png> <allawi.png> <saao.png> <albaz.png>\\n");',
    'fprintf(stderr, "Usage: <date> phase-debug | <date> map5|map5-smart evening <odeh.png> <yallop.png> <allawi.png> <saao.png> <albaz.png>\\n");',
    'usage')
route='''    if (!strcmp(argv[2], "map5")) {
        if (argc != 9) return 1;
        if (strcmp(argv[3], "evening")) return 1;
        return render_map5_evening(time, argv[4], argv[5], argv[6], argv[7], argv[8]);
    }
    fprintf(stderr, "Invalid command. Production R21 supports MAP5 only.\\n");'''
route2='''    if (!strcmp(argv[2], "map5")) {
        if (argc != 9) return 1;
        if (strcmp(argv[3], "evening")) return 1;
        return render_map5_evening(time, argv[4], argv[5], argv[6], argv[7], argv[8]);
    }
    if (!strcmp(argv[2], "map5-smart")) {
        if (argc != 9) return 1;
        if (strcmp(argv[3], "evening")) return 1;
        return render_map5_smart_evening(time, argv[4], argv[5], argv[6], argv[7], argv[8]);
    }
    fprintf(stderr, "Invalid command. Production R22 supports MAP5 and MAP5-SMART only.\\n");'''
one(route,route2,'route')

p.write_bytes(s.encode('utf-8'))
print('wrote',p)
