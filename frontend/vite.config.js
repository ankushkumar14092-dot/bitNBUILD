import {defineConfig} from 'vite';
import react from '@vitejs/plugin-react';
export default defineConfig({
  plugins:[react()],
 server:{host:'0.0.0.0',allowedHosts:true,proxy:{'/api':{target:'http://127.0.0.1:8000',changeOrigin:true,rewrite:path=>path.replace(/^\/api/,'')}}},
  build:{rolldownOptions:{output:{codeSplitting:{groups:[{name:'charts',test:/node_modules\/(recharts|d3-|victory)/},{name:'react-vendor',test:/node_modules\/(react|react-dom|scheduler)\//}]}}}}
});
