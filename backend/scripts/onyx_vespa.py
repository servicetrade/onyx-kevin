"""
Vespa Debugging Tool!

Usage:
  python vespa_debug_tool.py --action <action> [options]

Actions:
  config      : Print Vespa configuration
  connect     : Check Vespa connectivity
  list_apps   : List Vespa applications
  list_docs   : List documents
  search      : Search documents
  update      : Update a document
  delete      : Delete a document
  get_acls    : Get document ACLs

Options:
  --tenant-id     : Tenant ID
  --connector-id  : Connector ID
  --n             : Number of documents (default 10)
  --query         : Search query
  --doc-id        : Document ID
  --fields        : Fields to update (JSON)

Example: (gets docs for a given tenant id and connector id)
  python vespa_debug_tool.py --action list_docs --tenant-id my_tenant --connector-id 1 --n 5
"""
import argparse
import json
from typing import Any
from typing import Dict
from typing import List

from onyx.db.connector_credential_pair import get_connector_credential_pair_from_id
from onyx.db.engine import get_session_with_tenant
from onyx.db.search_settings import get_current_search_settings
from onyx.document_index.vespa.shared_utils.utils import get_vespa_http_client
from onyx.document_index.vespa_constants import DOCUMENT_ID_ENDPOINT
from onyx.document_index.vespa_constants import SEARCH_ENDPOINT
from onyx.document_index.vespa_constants import VESPA_APP_CONTAINER_URL
from onyx.document_index.vespa_constants import VESPA_APPLICATION_ENDPOINT


def print_vespa_config():
    """Prints the Vespa configuration URLs."""
    print(f"Vespa Application Endpoint: {VESPA_APPLICATION_ENDPOINT}")
    print(f"Vespa App Container URL: {VESPA_APP_CONTAINER_URL}")
    print(f"Vespa Search Endpoint: {SEARCH_ENDPOINT}")
    print(f"Vespa Document ID Endpoint: {DOCUMENT_ID_ENDPOINT}")


def check_vespa_connectivity():
    """
    Checks connectivity to several Vespa endpoints and prints the status
    code and a snippet of the response.
    """
    endpoints = [
        f"{VESPA_APPLICATION_ENDPOINT}/ApplicationStatus",
        f"{VESPA_APPLICATION_ENDPOINT}/tenant",
        f"{VESPA_APPLICATION_ENDPOINT}/tenant/default/application/",
        f"{VESPA_APPLICATION_ENDPOINT}/tenant/default/application/default",
    ]

    for endpoint in endpoints:
        try:
            with get_vespa_http_client() as client:
                response = client.get(endpoint)
                print(f"Successfully connected to Vespa at {endpoint}")
                print(f"Status code: {response.status_code}")
                print(f"Response: {response.text[:200]}...")
        except Exception as e:
            print(f"Failed to connect to Vespa at {endpoint}: {str(e)}")

    print("Vespa connectivity check completed.")


def list_vespa_applications():
    """Lists all Vespa applications."""
    url = f"{VESPA_APPLICATION_ENDPOINT}/tenant"
    try:
        with get_vespa_http_client() as client:
            response = client.get(url)
            response.raise_for_status()
            applications = response.json()
            print("Vespa Applications:")
            print(json.dumps(applications, indent=2))
    except Exception as e:
        print(f"Failed to list Vespa applications: {str(e)}")


def get_vespa_info() -> Dict[str, Any]:
    """
    Retrieves information about the default Vespa application.

    Returns:
        A dictionary with the JSON response containing information about
        the default application.
    """
    url = f"{VESPA_APPLICATION_ENDPOINT}/tenant/default/application/default"
    with get_vespa_http_client() as client:
        response = client.get(url)
        response.raise_for_status()
        return response.json()


def get_index_name(tenant_id: str, connector_id: int) -> str:
    """
    Retrieves the index name for a given tenant and connector pair.

    Args:
        tenant_id: The tenant's ID.
        connector_id: The connector's ID.

    Returns:
        The index name (e.g., "public" or a custom index name).
    """
    with get_session_with_tenant(tenant_id=tenant_id) as db_session:
        cc_pair = get_connector_credential_pair_from_id(db_session, connector_id)
        if not cc_pair:
            raise ValueError(f"No connector found for id {connector_id}")
        search_settings = get_current_search_settings(db_session)
        return search_settings.index_name if search_settings else "public"


def query_vespa(yql: str) -> List[Dict[str, Any]]:
    """
    Performs a Vespa query using YQL syntax.

    Args:
        yql: The YQL query string.

    Returns:
        A list of documents (dictionaries) returned by Vespa.
    """
    params = {
        "yql": yql,
        "timeout": "10s",
    }
    with get_vespa_http_client() as client:
        response = client.get(SEARCH_ENDPOINT, params=params)
        response.raise_for_status()
        return response.json()["root"]["children"]


def get_first_n_documents(n: int = 10) -> List[Dict[str, Any]]:
    """
    Retrieves the first N documents by running a simple 'select all' query.

    Args:
        n: The number of documents to retrieve.

    Returns:
        A list of the first N document dictionaries.
    """
    yql = f"select * from sources * where true limit {n};"
    return query_vespa(yql)


def print_documents(documents: List[Dict[str, Any]]) -> None:
    """
    Pretty-prints a list of documents.

    Args:
        documents: The list of document dictionaries to print.
    """
    for doc in documents:
        print(json.dumps(doc, indent=2))
        print("-" * 80)


def get_documents_for_tenant_connector(
    tenant_id: str, connector_id: int, n: int = 10
) -> None:
    """
    Retrieves and prints the first N documents for a specific tenant and connector.

    Args:
        tenant_id: The tenant's ID.
        connector_id: The connector's ID.
        n: The number of documents to retrieve.
    """
    get_index_name(tenant_id, connector_id)
    documents = get_first_n_documents(n)
    print(f"First {n} documents for tenant {tenant_id}, connector {connector_id}:")
    print_documents(documents)


def search_documents(
    tenant_id: str, connector_id: int, query: str, n: int = 10
) -> None:
    """
    Performs a search query against a specific tenant and connector, printing the results.

    Args:
        tenant_id: The tenant's ID.
        connector_id: The connector's ID.
        query: The search query string.
        n: The number of results to retrieve.
    """
    index_name = get_index_name(tenant_id, connector_id)
    yql = f"select * from sources {index_name} where userInput(@query) limit {n};"
    documents = query_vespa(yql)
    print(f"Search results for query '{query}':")
    print_documents(documents)


def update_document(
    tenant_id: str, connector_id: int, doc_id: str, fields: Dict[str, Any]
) -> None:
    """
    Updates a specific document with new field values.

    Args:
        tenant_id: The tenant's ID.
        connector_id: The connector's ID.
        doc_id: The document ID.
        fields: A dictionary of field names and values to update.
    """
    index_name = get_index_name(tenant_id, connector_id)
    url = DOCUMENT_ID_ENDPOINT.format(index_name=index_name) + f"/{doc_id}"
    update_request = {"fields": {k: {"assign": v} for k, v in fields.items()}}

    with get_vespa_http_client() as client:
        response = client.put(url, json=update_request)
        response.raise_for_status()
        print(f"Document {doc_id} updated successfully")


def delete_document(tenant_id: str, connector_id: int, doc_id: str) -> None:
    """
    Deletes a specific document.

    Args:
        tenant_id: The tenant's ID.
        connector_id: The connector's ID.
        doc_id: The document ID.
    """
    index_name = get_index_name(tenant_id, connector_id)
    url = DOCUMENT_ID_ENDPOINT.format(index_name=index_name) + f"/{doc_id}"

    with get_vespa_http_client() as client:
        response = client.delete(url)
        response.raise_for_status()
        print(f"Document {doc_id} deleted successfully")


def list_documents(n: int = 10):
    """
    Retrieves and prints the first N documents from any source.

    Args:
        n: The number of documents to retrieve.
    """
    yql = f"select * from sources * where true limit {n};"
    url = f"{VESPA_APP_CONTAINER_URL}/search/"
    params = {
        "yql": yql,
        "timeout": "10s",
    }
    try:
        with get_vespa_http_client() as client:
            response = client.get(url, params=params)
            response.raise_for_status()
            documents = response.json()["root"]["children"]
            print(f"First {n} documents:")
            print_documents(documents)
    except Exception as e:
        print(f"Failed to list documents: {str(e)}")


def get_document_acls(tenant_id: str, connector_id: int, n: int = 10) -> None:
    """
    Retrieves and prints Access Control Lists (ACLs) for documents belonging
    to a specific tenant and connector.

    Args:
        tenant_id: The tenant's ID.
        connector_id: The connector's ID.
        n: The number of documents to retrieve.
    """
    index_name = get_index_name(tenant_id, connector_id)
    yql = f"select documentid, access_control_list from sources {index_name} where true limit {n};"
    documents = query_vespa(yql)
    print(f"ACLs for {n} documents from tenant {tenant_id}, connector {connector_id}:")
    for doc in documents:
        print(f"Document ID: {doc['fields']['documentid']}")
        print(
            f"ACL: {json.dumps(doc['fields'].get('access_control_list', {}), indent=2)}"
        )
        print("-" * 80)


def main():
    parser = argparse.ArgumentParser(description="Vespa debugging tool")
    parser.add_argument(
        "--action",
        choices=[
            "config",
            "connect",
            "list_apps",
            "list_docs",
            "search",
            "update",
            "delete",
            "get_acls",
        ],
        required=True,
        help="Action to perform",
    )
    parser.add_argument(
        "--tenant-id", help="Tenant ID (for update, delete, and get_acls actions)"
    )
    parser.add_argument(
        "--connector-id",
        type=int,
        help="Connector ID (for update, delete, and get_acls actions)",
    )
    parser.add_argument(
        "--n",
        type=int,
        default=10,
        help="Number of documents to retrieve (for list_docs, search, update, and get_acls actions)",
    )
    parser.add_argument("--query", help="Search query (for search action)")
    parser.add_argument("--doc-id", help="Document ID (for update and delete actions)")
    parser.add_argument(
        "--fields", help="Fields to update, in JSON format (for update action)"
    )

    args = parser.parse_args()

    print(f"Debug: tenant_id = {args.tenant_id}, connector_id = {args.connector_id}")

    if args.action == "config":
        print_vespa_config()
    elif args.action == "connect":
        check_vespa_connectivity()
    elif args.action == "list_apps":
        list_vespa_applications()
    elif args.action == "list_docs":
        # If tenant_id and connector_id are provided, list docs for that tenant/connector.
        # Otherwise, list documents from any source.
        if args.tenant_id and args.connector_id:
            get_documents_for_tenant_connector(
                args.tenant_id, args.connector_id, args.n
            )
        else:
            list_documents(args.n)
    elif args.action == "search":
        if not args.query:
            parser.error("--query is required for search action")
        search_documents(args.tenant_id, args.connector_id, args.query, args.n)
    elif args.action == "update":
        if not args.doc_id or not args.fields:
            parser.error("--doc-id and --fields are required for update action")
        fields = json.loads(args.fields)
        update_document(args.tenant_id, args.connector_id, args.doc_id, fields)
    elif args.action == "delete":
        if not args.doc_id:
            parser.error("--doc-id is required for delete action")
        delete_document(args.tenant_id, args.connector_id, args.doc_id)
    elif args.action == "get_acls":
        if not args.tenant_id or args.connector_id is None:
            parser.error(
                "--tenant-id and --connector-id are required for get_acls action"
            )
        get_document_acls(args.tenant_id, args.connector_id, args.n)


if __name__ == "__main__":
    main()
