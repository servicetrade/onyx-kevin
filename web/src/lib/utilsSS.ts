import { cookies } from "next/headers";
import { HOST_URL, INTERNAL_URL } from "./constants";

export function buildClientUrl(path: string) {
  if (path.startsWith("/")) {
    return `${HOST_URL}${path}`;
  }
  return `${HOST_URL}/${path}`;
}

export function buildUrl(path: string) {
  if (path.startsWith("/")) {
    return `${INTERNAL_URL}${path}`;
  }
  return `${INTERNAL_URL}/${path}`;
}

/**
 * A utility class for building and manipulating URLs with parameters
 */
export class UrlBuilder {
  private url: URL;

  /**
   * Create a new UrlBuilder instance
   * @param baseUrl The base URL to build upon
   */
  constructor(baseUrl: string) {
    try {
      this.url = new URL(baseUrl);
    } catch (e) {
      // Handle relative URLs by prepending a base
      this.url = new URL(baseUrl, "http://placeholder.com");
    }
  }

  /**
   * Add a parameter to the URL
   * @param key Parameter name
   * @param value Parameter value
   * @returns The UrlBuilder instance for chaining
   */
  addParam(key: string, value: string | number | boolean): UrlBuilder {
    this.url.searchParams.set(key, String(value));
    return this;
  }

  /**
   * Add multiple parameters to the URL
   * @param params Object containing key-value pairs to add as parameters
   * @returns The UrlBuilder instance for chaining
   */
  addParams(params: Record<string, string | number | boolean>): UrlBuilder {
    Object.entries(params).forEach(([key, value]) => {
      this.url.searchParams.set(key, String(value));
    });
    return this;
  }

  /**
   * Get the built URL as a string
   * @returns The complete URL string
   */
  toString(): string {
    // Extract just the path and query parts for relative URLs
    if (this.url.origin === "http://placeholder.com") {
      return `${this.url.pathname}${this.url.search}`;
    }
    return this.url.toString();
  }

  /**
   * Create a UrlBuilder from an internal API path
   * @param path The API path
   * @returns A new UrlBuilder instance
   */
  static fromInternalUrl(path: string): UrlBuilder {
    return new UrlBuilder(buildUrl(path));
  }

  /**
   * Create a UrlBuilder from a client-side path
   * @param path The client path
   * @returns A new UrlBuilder instance
   */
  static fromClientUrl(path: string): UrlBuilder {
    return new UrlBuilder(buildClientUrl(path));
  }
}

export async function fetchSS(url: string, options?: RequestInit) {
  const init = options || {
    credentials: "include",
    cache: "no-store",
    headers: {
      cookie: (await cookies())
        .getAll()
        .map((cookie) => `${cookie.name}=${cookie.value}`)
        .join("; "),
    },
  };
  return fetch(buildUrl(url), init);
}
