# gateway-startup.sh
#!/bin/bash

# Register Services
curl -i -X POST http://localhost:8001/services/ \
  --data "name=user-service" \
  --data "url=http://user-service:8081"

curl -i -X POST http://localhost:8001/services/ \
  --data "name=order-service" \
  --data "url=http://order-service:8082"

curl -i -X POST http://localhost:8001/services/ \
  --data "name=product-service" \
  --data "url=http://product-service:8083"

curl -i -X POST http://localhost:8001/services/ \
  --data "name=inventory-service" \
  --data "url=http://inventory-service:8084"

curl -i -X POST http://localhost:8001/services/ \
  --data "name=notification-service" \
  --data "url=http://notification-service:8085"

curl -i -X POST http://localhost:8001/services/ \
  --data "name=payment-service" \
  --data "url=http://payment-service:8086"

curl -i -X POST http://localhost:8001/services/ \
  --data "name=spec-combiner" \
  --data "url=http://spec-combiner:9000"

# Register Routes
curl -i -X POST http://localhost:8001/services/user-service/routes \
  --data "paths[]=/user-service"

curl -i -X POST http://localhost:8001/services/order-service/routes \
  --data "paths[]=/order-service"

curl -i -X POST http://localhost:8001/services/product-service/routes \
  --data "paths[]=/product-service"

curl -i -X POST http://localhost:8001/services/inventory-service/routes \
  --data "paths[]=/inventory-service"

curl -i -X POST http://localhost:8001/services/notification-service/routes \
  --data "paths[]=/notification-service"

curl -i -X POST http://localhost:8001/services/payment-service/routes \
  --data "paths[]=/payment-service"

curl -i -X POST http://localhost:8001/services/spec-combiner/routes \
  --data "paths[]=/specs-combiner"

