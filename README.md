# odoo-tutorial
### Access permission
```
mkdir addons && sudo chmod -R 777 addons 
```
```
sudo chmod -R 777 config
```
### Start service
```
docker-compose up --build
```
### Activate container env
```
docker exec -it <container id> bash
```
### Create odoo module
```
odoo scaffold add_product /mnt/extra-addons
```
