class TrieNode:
    def __init__(self):
        self.children = {}
        self.path_param_node = None
        self.path_param_name = None
        self.wildcard_node = None
        self.handler = None

    def __repr__(self):
        return f"TrieNode({self.children}, {self.path_param_node}, {self.path_param_name}, {self.wildcard_node}, {self.handler})"


class Router:
    def __init__(self):
        # root node is the first node in the trie - level 0
        self.root = TrieNode()

    def add_route(self, method, route, handler):
        # roote node will have the HTTP method as a child node - level 1
        if method not in self.root.children:
            self.root.children[method] = TrieNode()

        # start at the HTTP method node
        node = self.root.children[method]

        # split the route into path segments
        for path_segment in route.split("/"):
            # if the route path just contains "/"
            if not path_segment:
                continue
            # if the path segment is a path parameter
            if path_segment[0] == ":":
                if not node.path_param_node:
                    node.path_param_node = TrieNode()
                    node.path_param_name = path_segment[1:]
                node = node.path_param_node
            # if the path segment is a wildcard
            elif path_segment == "*":
                if not node.wildcard_node:
                    node.wildcard_node = TrieNode()
                node = node.wildcard_node
            # if the path segment is a static path
            else:
                if path_segment not in node.children:
                    node.children[path_segment] = TrieNode()
                node = node.children[path_segment]
        # set the handler of the leaf node
        node.handler = handler

    def lookup(self, method, route):
        # HTTP method node
        node = self.root.children.get(method)

        # if the HTTP method node does not exist
        if not node:
            return None, {}

        params = {}
        # split the route into path segments
        for segment in route.split("/"):
            if not segment:
                continue
            # if the path segment is a static path
            if segment in node.children:
                node = node.children[segment]
            # if the path segment is a path parameter
            elif node.path_param_node:
                node = node.path_param_node
                params[node.path_param_name] = segment
            # if the path segment is a wildcard
            elif node.wildcard_node:
                node = node.wildcard_node
                params["*"] = segment

        if params == {} and node.handler is None:
            lambda_handler = lambda: print("404 Not Found")
        else:
            node.handler()


if __name__ == "__main__":
    router = Router()
    router.add_route("GET", "/", lambda: print("root handler"))
    router.add_route("GET", "/users", lambda: print("users handler"))
    router.add_route("GET", "/users/:name", lambda: print("users name handler"))
    router.add_route(
        "GET", "/users/:name/settings", lambda: print("users settings handler")
    )
    router.add_route("GET", "/users/*", lambda: print("users wildcard handler"))
    router.add_route("POST", "/users", lambda: print("users POST handler"))
    router.add_route("PATCH", "/users/:name", lambda: print("users name POST handler"))

    router.lookup("GET", "/")  # root handler
    router.lookup("GET", "/users")  # users handler
    router.lookup("GET", "/users/john")  # users name handler
    router.lookup("GET", "/users/john/settings")  # users settings handler
    router.lookup("GET", "/users/john/friends")  # users wildcard handler
    router.lookup("POST", "/users")  # users POST handler
    router.lookup("PATCH", "/users/john")  # users name POST handler
    router.lookup("GET", "/posts")  # 404 Not Found
