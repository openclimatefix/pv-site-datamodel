# TODO


 ## Test

To run tests use
```bash
docker stop $(docker ps -a -q); true
docker-compose -f test-docker-compose.yml build tests
docker-compose -f test-docker-compose.yml run tests
```