VERSION := 7.12.0
NAMESPACE := elastic


install: check elastic kibana filebeat

check:
	if ! helm repo list | grep elastic &> /dev/null; then \
		helm repo add https://helm.elastic.co; \
		helm repo update; \
	fi

elastic:
	helm upgrade \
		--install elasticsearch elastic/elasticsearch \
		--create-namespace \
		--set replicas=1 \
		--set resources=null \
		--set volumeClaimTemplate.resources.requests.storage=1Gi \
		--set imageTag=$(VERSION) \
		--namespace $(NAMESPACE)

kibana:
	helm upgrade \
		--install kibana elastic/kibana \
		--create-namespace \
		--set resources=null \
		--set imageTag=$(VERSION) \
		--namespace $(NAMESPACE)

filebeat:
	helm upgrade \
		--install filebeat elastic/filebeat \
		--values filebeat-values.yaml \
		--set daemonset.resources=null \
		--set imageTag=$(VERSION) \
		--namespace kube-system


proxy-kibana:
	@echo '-> http://localhost:5601/'
	kubectl port-forward svc/kibana-kibana "5601:5601" -n $(NAMESPACE)
