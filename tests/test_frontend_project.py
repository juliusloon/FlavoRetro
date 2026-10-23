"""Frontend source/build contracts. No web server, chemistry assets, or new search."""
import importlib.util
import json
from pathlib import Path
import tempfile
import unittest

SPEC=importlib.util.spec_from_file_location('frontend_build',Path(__file__).resolve().parents[1]/'scripts/frontend.py')
frontend=importlib.util.module_from_spec(SPEC);SPEC.loader.exec_module(frontend)

class FrontendProject(unittest.TestCase):
    def setUp(self):
        self.tmp=tempfile.TemporaryDirectory();self.addCleanup(self.tmp.cleanup);self.root=Path(self.tmp.name)
        self.put('web/frontend.json',json.dumps({'schema_version':1,'shell':'src/shell.html','routes':'routes.json','scripts':['@routes','src/core/router.js'],'styles':['styles/base.css'],'outputs':{'html':'index.html','js':'app.js','css':'style.css'}}))
        self.put('web/routes.json',json.dumps({'schema_version':1,'pages':[{'id':'home','title':'Home','template':'src/pages/home/view.html','primary':True}],'subpages':[{'path':'#/home','state':[],'purpose':'Home'}]}))
        self.put('web/src/shell.html','<!doctype html><a data-tab="home"></a><main><!-- @include src/pages/home/view.html --></main>')
        self.put('web/src/pages/home/view.html','<section id="home" class="page"><h1 id="home-title">Home</h1></section>')
        self.put('web/src/core/router.js','const marker = 1;\n');self.put('web/styles/base.css',':root { --gap: 20px; }\n')
    def put(self,name,content):
        p=self.root/name;p.parent.mkdir(parents=True,exist_ok=True);p.write_text(content)
    def mutate_json(self,name,change):
        p=self.root/name;data=json.loads(p.read_text());change(data);p.write_text(json.dumps(data))
    def test_build_is_deterministic_and_includes_page_sources(self):
        a=frontend.render_assets(self.root);self.assertEqual(a,frontend.render_assets(self.root));self.assertIn('id="home-title"',a['index.html']);self.assertNotIn('@include',a['index.html']);self.assertIn('ROUTE_DEFINITIONS',a['app.js'])
    def test_drift_detects_runtime_and_packaged_outputs(self):
        assets=frontend.render_assets(self.root)
        for name,content in assets.items():
            self.put('web/'+name,content);self.put('flavoretro/assets/web/'+name,content)
        self.assertEqual(frontend.differences(self.root,assets),[])
        self.put('web/app.js','stale');self.assertEqual(frontend.differences(self.root,assets),['web/app.js'])
    def test_include_cycle_is_rejected(self):
        self.put('web/src/pages/home/view.html','<!-- @include src/shell.html -->')
        with self.assertRaisesRegex(frontend.FrontendError,'include cycle'):frontend.render_assets(self.root)
    def test_outside_source_path_is_rejected(self):
        with self.assertRaisesRegex(frontend.FrontendError,'outside'):frontend.source_path(self.root/'web','../external.js')
    def test_duplicate_html_id_is_rejected(self):
        self.put('web/src/pages/home/view.html','<section id="home" class="page"><div id="home"></div></section>')
        with self.assertRaisesRegex(frontend.FrontendError,'duplicate HTML id'):frontend.render_assets(self.root)
    def test_route_and_template_drift_is_rejected(self):
        self.mutate_json('web/routes.json',lambda d:d['pages'][0].update(id='other'))
        with self.assertRaisesRegex(frontend.FrontendError,'registry disagree'):frontend.render_assets(self.root)
    def test_duplicate_script_is_rejected(self):
        self.mutate_json('web/frontend.json',lambda d:d['scripts'].append('src/core/router.js'))
        with self.assertRaisesRegex(frontend.FrontendError,'duplicate source'):frontend.render_assets(self.root)
    def test_scaffold_registers_a_page_and_escapes_its_title(self):
        plan=frontend.scaffold_plan(self.root,'new-page','<Title & example>')
        for name,content in plan.items():self.put('web/'+name,content)
        built=frontend.render_assets(self.root)
        self.assertIn('id="new-page"',built['index.html']);self.assertIn('&lt;Title &amp; example&gt;',built['index.html']);self.assertIn('PageRegistry.register("new-page"',built['app.js'])
    def test_scaffold_rejects_invalid_baseline_before_editing(self):
        self.put('web/src/pages/home/view.html','<section id="home" class="page"><div id="home"></div></section>')
        manifest=(self.root/'web/frontend.json').read_bytes()
        with self.assertRaisesRegex(frontend.FrontendError,'duplicate HTML id'):frontend.scaffold_plan(self.root,'reports','Reports')
        self.assertEqual((self.root/'web/frontend.json').read_bytes(),manifest)
        self.assertFalse((self.root/'web/src/pages/reports').exists())
    def test_scaffold_rejects_existing_and_invalid_pages(self):
        for page in ['home','../other','UPPER']:
            with self.assertRaises(frontend.FrontendError):frontend.scaffold_plan(self.root,page,'Title')
    def test_breadcrumb_cannot_be_reintroduced_by_a_template(self):
        self.put('web/src/pages/home/view.html','<section id="home" class="page"><nav id="page-breadcrumb"></nav></section>')
        with self.assertRaisesRegex(frontend.FrontendError,'breadcrumb'):frontend.render_assets(self.root)

if __name__=='__main__':unittest.main()
