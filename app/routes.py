from flask import send_from_directory, Response
from flask_cors import cross_origin
from app import app
from app.auth import requires_auth, requires_scope
from livestream.stream import generate

@app.route('/api/video/<path:path>')
@cross_origin(headers=["Content-Type", "Authorization"])
@requires_auth
def get_video(path):
	return send_from_directory('../assets', path)

@app.route('/api/livestream')
@cross_origin(headers=["Content-Type", "Authorization"])
@requires_auth
def video_feed():
	# return the response generated along with the specific media type (mime type)
	return Response(generate(), mimetype="multipart/x-mixed-replace; boundary=frame")
