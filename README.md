# Agentic AI Product Research & Purchase Decision System

An Agentic AI Product Research and Purchase Decision System that helps users research products and make informed purchase decisions using natural-language queries.

The application combines LangGraph, MCP, FastMCP, Groq, Tavily, and FastAPI to automate product discovery, price research, review analysis, and product comparisons.

## Project Overview

When users want to purchase a product, they usually need to search across multiple websites for product specifications, prices, reviews, and alternatives.

This project automates these research activities through an AI-powered workflow.

The user enters a natural-language request, and the system:

1. Extracts the user's requirements.
2. Searches for relevant products and specifications.
3. Retrieves price and availability information.
4. Searches for product reviews, pros, and cons.
5. Finds product comparisons and alternatives.
6. Uses an LLM to analyze the collected information.
7. Generates an evidence-based purchase recommendation.

## Project Objective

The main objective is to build an AI-powered shopping research assistant that reduces manual product research and provides structured information based on the user's requirements.

The system is designed to consider factors such as:

* Product category
* Budget
* Intended usage
* Required features
* Preferred features
* Product limitations
* Alternatives and comparisons

## System Architecture

                    USER
                     |
             FastAPI Web Interface
                     |
             LangGraph Workflow
                     |
          +----------+----------+
          |                     |
  Requirements Node       Research Node
  (Groq LLM)                   |
  
                    Remote MCP Server
                         (FastMCP)
                               |
       -------------------------------------------------       
       |                       |                       |
 Product Search          Price Search           Review Search
       |                       |                       |
       -------------------------------------------------
                               |
                               
                       Tavily Web Search
                               
                               |
                    Research Results
                               |
                    Recommendation Node
                         (Groq LLM)
                               |
                     Final Research Report

## Workflow

### 1. User Query

The user enters a request such as:

I need a laptop for Python and machine learning under ₹70000 in India.

### 2. Requirements Extraction

The requirements node uses the Groq LLM to extract relevant details into a structured JSON format.

The extracted information includes:

* Product type
* Budget
* Purpose
* Must-have features
* Preferred features
* Features to avoid
* Important considerations

### 3. Product Research

The research node calls four MCP tools:

| Tool                | Purpose                                        |
| ------------------- | ---------------------------------------------- |
| search_products   | Searches for products and specifications       |
| search_prices     | Searches for current prices and availability   |
| search_reviews    | Searches for reviews, pros, cons, and problems |
| search_comparison | Searches for comparisons and alternatives      |

These tools are accessed through the remote FastMCP server.

### 4. Web Search

The FastMCP server uses the Tavily Search API to retrieve relevant web information.

The search results are formatted with:

* Source title
* Source URL
* Relevant content

### 5. Information Analysis

The recommendation node sends the user's requirements and collected research data to the Groq LLM.

The LLM is instructed to:

* Use evidence from the collected information.
* Avoid inventing product details.
* Respect the user's requirements.
* Mark missing information as `Not verified`.
* Identify conflicting evidence.
* Include relevant pros, cons, and alternatives.

### 6. Final Recommendation

The application returns a plain-text report containing:

* Recommended product
* Current price
* Why the product matches
* Key details
* Pros and cons
* Verification status
* Alternatives
* Final recommendation

## Technology Stack

| Technology          | Usage                                          |
| ------------------- | ---------------------------------------------- |
| Python              | Core programming language                      |
| LangGraph           | Workflow orchestration                         |
| MCP                 | Standard tool communication protocol           |
| FastMCP             | MCP server and tool implementation             |
| Groq                | LLM-based requirements extraction and analysis |
| Tavily              | Web search and information retrieval           |
| FastAPI             | Backend API and web application                |
| HTML/CSS/JavaScript | Frontend interface                             |
| python-dotenv       | Environment variable management                |
| asyncio             | Concurrent research tool calls                 |

## Example Queries

Best laptop for programming under ₹70000 in India

I need an office chair under ₹20000 for long working hours.

Compare smartphones under ₹30000 with good cameras and battery life.

Find headphones for travel and daily use under ₹5000.

## MCP Tools

### search_products

Searches for matching products and relevant specifications.

### search_prices

Searches for current product prices and availability across relevant sources.

### search_reviews

Searches for expert reviews, user feedback, advantages, disadvantages, and problems.

### search_comparison

Searches for product alternatives and comparison information.

## LangGraph Workflow

The project uses a sequential LangGraph workflow with three main nodes:

START -> Requirements Extraction -> Product Research -> Recommendation Generation -> END

### Requirements Node

Uses the Groq LLM to extract structured information from the user's query.

### Research Node

Calls the four shopping MCP tools concurrently using asynchronous execution.

### Recommendation Node

Analyzes the research results and generates the final report according to evidence-based output rules.

## Evidence and Limitations

The system instructs the LLM not to invent product details and to mark missing information as `Not verified`.

However, the generated report depends on the quality and completeness of retrieved search results.

Current limitations include:

* Web search results may be incomplete.
* Product prices and availability can change.
* Search results may contain conflicting information.
* LLM-generated summaries may require manual verification.
* The system does not guarantee product quality or purchasing outcomes.
* Product research is not a substitute for checking current information on official stores.

Users should verify important product details, prices, and availability before purchasing.

## Challenges Addressed

* Connecting a local LangGraph application to a remote MCP server.
* Integrating FastMCP tools with a shopping research workflow.
* Handling asynchronous calls to multiple research tools.
* Managing API keys through environment variables.
* Formatting retrieved web information for LLM analysis.
* Reducing unsupported product claims through explicit prompt instructions.
* Handling missing and unverified research information.

## Future Enhancements

* Add structured product data extraction.
* Add duplicate product detection.
* Add stronger source-level verification.
* Add price freshness and availability checks.
* Add product ranking based on user-defined criteria without relying only on LLM judgment.
* Add caching to reduce repeated searches.
* Add user preference memory.
* Add evaluation datasets for recommendation accuracy.
* Add a product comparison table in the frontend.
* Add source links and evidence passages to the final report.
