# Research-paper Approval System
A multi-role web application to streamline research paper submission and approval in an academic institution.

Features:

Role-based access: Faculty, HOD, Principal, Dean.

Faculty: Upload research papers and plagiarism reports.

HOD/Principal/Dean: Review, approve/reject, and add comments.

Automated workflow: Paper progresses through hierarchy upon approvals.

Unique ID generation: Each approved paper gets a unique publication ID (e.g., 25SVECW01).

Automated reporting: Publication reports shared with HOD, Principal, and Research Coordinator.

DOA Assignment: Approved papers receive a Document of Approval (DOA) number sent to faculty.

Suggested architecture: Workflow can be modeled as a graph data structure for tracking approvals and transitions.
