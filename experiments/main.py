from flask import Flask, request, Response
from prometheus_client.core import CounterMetricFamily, REGISTRY	
from prometheus_client import generate_latest, CONTENT_TYPE_LATEST, make_wsgi_app	

app = Flask(__name__)


class CustomServiceExporter:
	stored_auth_count = {"user1":1}
	def collect(self):
		CustomServiceExporter.stored_auth_count["user1"] = CustomServiceExporter.stored_auth_count["user1"] + 1 
		request_total = CounterMetricFamily(
			"authlog_per_user_total",
			"This is comment",
			labels = ["username"]
		)

		for username, count in self.stored_auth_count.items():
			request_total.add_metric([username], count)
		yield request_total


REGISTRY.register(CustomServiceExporter())



@app.route("/metric-receiver", methods=["POST"])
def track_metric():
	data = request.json
#	build_histo(...)
	return Response(status=200)
	
	
#def build_histo(...)

@app.route("/metrics")
def metrics():
	# return Response(status=200)
	return Response(generate_latest(), mimetype=CONTENT_TYPE_LATEST)

@app.route("/")
def index():
    return "Index!"

if __name__ == '__main__':
 
    # run() method of Flask class runs the application
    # on the local development server.
    app.run()






