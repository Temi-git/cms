class SimpleCorsMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response
        print(">>> SimpleCorsMiddleware is loaded")   # debug

    def __call__(self, request):
        print(">>> SimpleCorsMiddleware is running for:", request.path)  # debug
        
        response = self.get_response(request)
        
        response["Access-Control-Allow-Origin"] = "*"
        response["Access-Control-Allow-Methods"] = "GET, POST, OPTIONS, PUT, DELETE"
        response["Access-Control-Allow-Headers"] = "Content-Type, Authorization"
        
        return response