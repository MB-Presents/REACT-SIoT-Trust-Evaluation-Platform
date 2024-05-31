docker-compose build

docker-compose up setup


curl -ks -u elastic:changeme -XPUT "http://localhost:9200/_cluster/settings" -H 'Content-Type: application/json' -d'
{
  "persistent": {
  "ingest.geoip.downloader.enabled" : "false"
  }
}'

docker-compose up setup


docker-compose up 




<!-- curl -u elastic:changeme -XDELETE http://localhost:9200/.kibana_1  -->
<!-- curl -u elastic:changeme --request DELETE 'http://localhost:9200/.kibana_8.7.1_001' -->


- Write this in hte config file of elasticsearch
cluster.routing.allocation.disk.watermark.high: 95%
cluster.routing.allocation.disk.watermark.flood_stage: 97%

curl  -u elastic:changeme  http://localhost:9200/_cluster/health

{"cluster_name":"docker-cluster",
"status":"red",
"timed_out":false,
"number_of_nodes":1,
"number_of_data_nodes":1,
"active_primary_shards":14,
"active_shards":14,
"relocating_shards":0,
"initializing_shards":0,
"unassigned_shards":3,
"delayed_unassigned_shards":0,
"number_of_pending_tasks":0,
"number_of_in_flight_fetch":0,
"task_max_waiting_in_queue_millis":0,
"active_shards_percent_as_number":82.35294117647058}%   


xpack.license.self_generated.type: basic