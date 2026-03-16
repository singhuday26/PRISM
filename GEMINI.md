# 🏛 PRISM System Mandate & Architectural Rules

## 1. Core Architectural Constraints
- **Strict Layering**: Code must follow the path: `Route -> Service -> Model`. 
    - Routes handle ONLY request validation and response formatting.
    - Services handle all business logic and forecasting math.
    - Models/Repository handle all MongoDB interactions.
- **Dependency Injection**: Always use FastAPI `Depends()` for database sessions, authentication, and service initialization. No global database instances.

## 2. Technical Stack Guardrails (2026 Standards)
- **FastAPI**: Use Pydantic V2 `@field_validator` for data cleansing. All endpoints must return a documented `response_model`.
- **React 19**: 
    - Use `useActionState` and `useOptimistic` for form handling.
    - **No Local State Overload**: If state is shared between more than two components, move it to a dedicated Context Provider or a custom hook.
    - Strict TypeScript interfaces for all component props.
## 2. Technical Stack Guardrails (2026 Standards)
- **FastAPI**: Use Pydantic V2 `@field_validator` for data cleansing. All endpoints must return a documented `response_model`.
- **React 19**: 
    - Use `useActionState` and `useOptimistic` for form handling.
    - **No Local State Overload**: If state is shared between more than two components, move it to a dedicated Context Provider or a custom hook.
    - Strict TypeScript interfaces for all component props.
- **Data Science**: 
    - Time-series data must be validated for "Continuity" (no missing dates) before being passed to `Statsmodels`.
    - Offload long-running ARIMA calculations to a background task or a specialized worker.

## 3. The "FAANG-Standard" Quality Bar
- **Error Handling**: Never use bare `except:`. Every exception must be mapped to a custom `PRISMException` with a corresponding HTTP status code.
- **Complexity Guard**: Any function with a cyclomatic complexity > 10 must be refactored into smaller sub-services.
- **Documentation**: Every function must include a Google-style docstring explaining the 'Why', not just the 'What'.

## 4. Security & Compliance
- Never log PII (Personally Identifiable Information) or raw climate data source credentials.
- All MongoDB queries must use projection to return only the necessary fields.
