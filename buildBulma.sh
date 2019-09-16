#!/usr/bin/env bash
npm install
sass --no-source-map node_modules/bulma/sass/mosla.scss:static/styles/bulma.min.css --style compressed
#sass --no-source-map node_modules/bulma-switch/dist/css/bulma-switch.sass:static/styles/bulma-switch.min.css --style compressed
cp node_modules/chart.js/dist/Chart.min.js static/js/Chart.min.js
#cp node_modules/bulma-switch/dist/css/bulma-switch.min.css static/styles/bulma-switch.min.css
cp node_modules/chart.js/dist/Chart.min.css static/styles/Chart.min.css
cp node_modules/chartjs-plugin-dragdata/dist/chartjs-plugin-dragData.min.js static/js/chartjs-plugin-dragData.min.js
cp node_modules/json5/dist/index.min.js static/js/index.min.js
cp node_modules/jquery/dist/jquery.min.js static/js/jquery.min.js
cp node_modules/letteringjs/jquery.lettering.js static/js/jquery.lettering.js

cp node_modules/sortablejs/Sortable.js static/js/Sortable.js
cp node_modules/sortablejs/Sortable.min.js static/js/Sortable.min.js

cp node_modules/nouislider/distribute/nouislider.css static/styles/nouislider.css
cp node_modules/nouislider/distribute/nouislider.min.js static/js/nouislider.min.js

cp node_modules/@fortawesome/fontawesome-free/js/all.min.js static/js/fontawesome.min.js
#cp node_modules/@fortawesome/fontawesome-free/css/all.min.css static/style/fontawesome.min.css

rm static/js/all.min.js
rm static/styles/all.min.css
cd static/js

uglifyjs -c --output all.min.js -- jquery.min.js jquery.lettering.js Chart.min.js chartjs-plugin-dragData.min.js fontawesome.min.js error-chart.js autoscroll.js ajax-api.js index.min.js nouislider.min.js Sortable.min.js error_probs.js
cd ../styles
uglifycss --output all.min.css bulma.min.css infobox.css bootstrap-float-label.min.css balloon.min.css Chart.min.css overlay.css nouislider.css #fontawesome.min.js #bulma-switch.min.css
