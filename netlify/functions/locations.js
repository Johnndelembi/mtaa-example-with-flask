const { locations, children } = require("./data/locations.json");

exports.handler = async function (event) {
    if (event.httpMethod !== "GET") {
        return { statusCode: 405, headers: { Allow: "GET" }, body: "Method not allowed" };
    }
    const parameters = event.queryStringParameters || {};
    let result;
    if (Object.hasOwn(parameters, "path")) {
        const path = parameters.path.split("/").map(decodeURIComponent).join("/");
        result = children[path] || [];
    } else {
        const query = (parameters.q || "").trim().toLowerCase();
        result = query.length < 2 ? [] : locations.filter(location =>
            location.name.toLowerCase().includes(query)
        ).sort((a, b) =>
            Number(!a.name.toLowerCase().startsWith(query)) - Number(!b.name.toLowerCase().startsWith(query)) ||
            a.name.length - b.name.length ||
            (a.name.toLowerCase() < b.name.toLowerCase() ? -1 : a.name.toLowerCase() > b.name.toLowerCase() ? 1 : 0)
        ).slice(0, 8);
    }
    return {
        statusCode: 200,
        headers: { "Content-Type": "application/json; charset=utf-8" },
        body: JSON.stringify(result)
    };
};
