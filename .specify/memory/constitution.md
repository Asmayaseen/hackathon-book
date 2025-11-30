<!--
Sync Impact Report:
Version: 0.0.0 → 1.0.0 (Initial constitution creation)
Modified Principles: N/A (new)
Added Sections: All 6 core principles + Performance Standards + Governance
Removed Sections: None
Templates Requiring Updates: ✅ All templates will inherit these principles
Follow-up TODOs: None
-->

# Physical AI & Humanoid Robotics Textbook Constitution

## Core Principles

### I. Content Quality (NON-NEGOTIABLE)

**Technical Accuracy & Clarity**
- All technical content MUST be verified for accuracy before publication
- Explanations MUST be suitable for target learners (beginner to advanced levels)
- Code examples MUST include comprehensive inline comments and explanations
- Terminology MUST be consistent across all modules and chapters
- Complex concepts MUST be broken down with progressive examples
- All robotics/AI terms MUST be defined on first use

**Rationale**: Educational content quality directly impacts learning outcomes. Inaccurate or unclear content wastes learner time and damages credibility.

### II. Code Standards

**Clean, Documented, Secure Code**
- All code examples MUST be clean, well-structured, and follow language idioms
- NO hardcoded secrets, API keys, or credentials (use environment variables)
- Error handling MUST be present in all code examples (no silent failures)
- TypeScript code MUST use strict type safety
- Python code MUST use type hints (PEP 484)
- All functions MUST have docstrings explaining purpose, parameters, and return values
- Security best practices MUST be followed (input validation, sanitization, authentication)

**Rationale**: Students learn by example. Poor code examples teach bad habits. Security vulnerabilities in educational content create risk when students copy code to production.

### III. Testing Requirements (NON-NEGOTIABLE)

**Validated, Reproducible Content**
- All code examples MUST be tested and confirmed working before publication
- RAG chatbot responses MUST be validated for accuracy (>85% correctness)
- Authentication flows MUST be security-tested (no bypass vulnerabilities)
- Content generation MUST be reproducible (same inputs → same outputs)
- Integration tests MUST cover: chatbot queries, user authentication, content personalization, translation accuracy
- Test data MUST be provided for all examples

**Rationale**: Broken code examples frustrate learners and waste time. Un-tested AI features create poor user experience. Test-first ensures reliability.

### IV. User Experience

**Fast, Accessible, Intuitive Design**
- Page load times MUST be < 3 seconds (measured on 3G connection)
- Design MUST be responsive for mobile, tablet, and desktop
- Content MUST meet WCAG 2.1 AA accessibility standards
- Navigation between modules MUST be intuitive (max 3 clicks to any chapter)
- Chatbot integration MUST be seamless (no page reloads, instant responses)
- Search functionality MUST return relevant results in < 1 second
- Text selection for chatbot queries MUST work on first attempt
- Progress indicators MUST be visible for all loading operations

**Rationale**: Poor UX leads to learner abandonment. Accessibility ensures inclusive education. Speed impacts engagement and retention.

### V. AI Integration

**Accurate, Private, Ethical AI**
- Prompt engineering MUST follow best practices (clear context, specific instructions, output formatting)
- RAG accuracy MUST be > 85% (validated through test queries)
- Personalization MUST respect user privacy (no sensitive data logging)
- Translation MUST maintain technical accuracy (preserve technical terms, code blocks)
- AI-generated content MUST be reviewed before publication
- Chatbot responses MUST cite sources (chapter/section references)
- User data MUST NOT be used for AI training without explicit consent
- AI limitations MUST be disclosed to users (e.g., "AI-generated content may contain errors")

**Rationale**: AI accuracy impacts trust. Privacy violations violate user rights. Ethical AI use builds long-term credibility.

### VI. Performance Standards

**Scalable, Efficient Operations**
- Build time MUST be < 2 minutes (Docusaurus production build)
- API response time MUST be < 500ms (95th percentile)
- Chatbot queries MUST return in < 3 seconds (including RAG retrieval)
- System MUST support 100+ concurrent users without degradation
- Database queries MUST be optimized (indexed fields, query optimization)
- Vector search in Qdrant MUST return top 5 results in < 200ms
- Frontend bundle size MUST be < 500KB (gzipped)
- Images MUST be optimized (WebP format, lazy loading)

**Rationale**: Performance impacts user experience and operational costs. Slow systems frustrate users. Scalability ensures reliability under load.

## Development Workflow

**Quality Gates & Review Process**

1. **Content Creation**:
   - Write specification using `/sp.specify`
   - Create technical plan using `/sp.plan`
   - Generate tasks using `/sp.tasks`
   - Implement using `/sp.implement`

2. **Code Review Requirements**:
   - All code examples MUST be peer-reviewed
   - Security review MUST be performed for authentication/authorization code
   - AI-generated content MUST be human-reviewed for accuracy

3. **Testing Gates**:
   - Unit tests MUST pass before merge
   - Integration tests MUST pass before deployment
   - RAG accuracy MUST be validated with test queries

4. **Deployment Approval**:
   - Frontend build MUST complete without errors
   - Backend health checks MUST pass
   - Database migrations MUST be tested in staging

## Security Requirements

**Authentication & Data Protection**

- User passwords MUST be hashed with bcrypt (min 10 rounds)
- Session tokens MUST be HTTP-only, Secure, SameSite cookies
- API endpoints MUST validate authentication before processing
- User data MUST be encrypted at rest (database encryption)
- API keys MUST be stored in environment variables (never in code)
- HTTPS MUST be enforced for all connections
- Rate limiting MUST be implemented (max 100 requests/minute per user)
- SQL injection MUST be prevented (parameterized queries)
- XSS attacks MUST be prevented (input sanitization, CSP headers)

**Rationale**: Security breaches damage user trust and violate privacy. Educational platforms handle sensitive user data (progress, preferences).

## Governance

**Constitution Authority & Amendment Process**

This constitution supersedes all other development practices and guidelines. All contributions MUST comply with these principles.

**Amendment Requirements**:
1. Amendments MUST be documented with rationale
2. Breaking changes MUST include migration plan
3. Version MUST be incremented according to semantic versioning:
   - MAJOR: Backward incompatible principle changes
   - MINOR: New principles or material expansions
   - PATCH: Clarifications, wording improvements

**Compliance Verification**:
- All pull requests MUST be reviewed for constitution compliance
- Complexity violations MUST be justified with documented rationale
- Deviations MUST be approved by project maintainers

**Enforcement**:
- Non-compliant code MUST NOT be merged
- Security violations MUST be fixed immediately
- Performance regressions MUST be addressed before deployment

**Version**: 1.0.0 | **Ratified**: 2025-11-29 | **Last Amended**: 2025-11-29
