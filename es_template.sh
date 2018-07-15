#!/usr/bin/bash

curl -XPUT "${ES_HOST}:9200/_template/metrics?pretty" -H 'Content-Type: application/json' -d'
{
  "template": "metrics*",
  "settings": {
    "number_of_shards": 1,
    "number_of_replicas": 0
  },
  "mappings": {
    "measurement": {
      "_source": {
        "enabled": true
      },
      "properties": {
        "temperature": {
          "type": "half_float"
        },
        "humidity": {
          "type": "half_float"
        },
        "pressure": {
	  "type": "half_float"
	},
        "co2": {
	  "type": "integer"
	},
	"uncertainty": {
	  "type": "half_float"
	}
      }
    }
  }
}
'

