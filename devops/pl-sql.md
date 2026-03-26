# pl-sql

Here’s a complete PL/SQL end-to-end revision guide you can use to brush up before interviews. It’s organized so you can skim fundamentals quickly and dive into advanced concepts as needed.

***

### 1️⃣ PL/SQL Basics

<br>

What is PL/SQL

* Oracle’s procedural extension of SQL.
* Combines SQL (data manipulation) with procedural features (variables, loops, conditions).
* Code is grouped into blocks: anonymous blocks or named program units (procedures, functions, packages).

<br>

Block Structure

```
DECLARE  -- optional
   -- variable declarations
BEGIN
   -- executable statements
EXCEPTION  -- optional
   -- error handling
END;
```

* Declarative Section: Define variables, constants, cursors.
* Executable Section: SQL & procedural statements.
* Exception Section: Handle runtime errors.

***

### 2️⃣ Data Types & Variables

* Scalar: NUMBER, VARCHAR2, DATE, BOOLEAN.
* Composite: RECORD, TABLE (Associative arrays).
* Reference: REF CURSOR.
* LOB: BLOB, CLOB.
* %TYPE and %ROWTYPE: Inherit column/table structure.

<br>

Example:

```
v_salary employees.salary%TYPE;
emp_record employees%ROWTYPE;
```

***

### 3️⃣ Control Structures

* Conditional: IF…THEN, CASE.
* Loops:
  * Simple LOOP ... END LOOP;
  * WHILE … LOOP
  * FOR i IN 1..10 LOOP

***

### 4️⃣ Cursors

<br>

Used to handle multi-row query results.

* Implicit Cursor: Automatically for DML (INSERT/UPDATE/DELETE/SELECT INTO).
* Explicit Cursor:

```
CURSOR c1 IS SELECT empno, ename FROM emp;
OPEN c1;
FETCH c1 INTO v_empno, v_ename;
CLOSE c1;
```

* Cursor FOR Loop (simpler):

```
FOR rec IN c1 LOOP
   DBMS_OUTPUT.PUT_LINE(rec.empno);
END LOOP;
```

* Parameterised Cursor: Pass parameters at runtime.

***

### 5️⃣ Procedures & Functions

* Procedure: Performs action, can return OUT parameters.
* Function: Must return a value, usable in SQL expressions.

<br>

Example Procedure:

```
CREATE OR REPLACE PROCEDURE raise_salary(p_id NUMBER, p_amt NUMBER) AS
BEGIN
   UPDATE employees SET salary = salary + p_amt WHERE employee_id = p_id;
END;
```

***

### 6️⃣ Packages

* Group related procedures/functions, variables, cursors.
* Specification: Public interface.
* Body: Implementation.
* Advantages: Encapsulation, reusability, better dependency management.

***

### 7️⃣ Triggers

* Fired automatically on DML/DDL/events.
* Types:
  * Row-level vs Statement-level
  * Before vs After
  * Instead Of (for views)
* Example:

```
CREATE OR REPLACE TRIGGER trg_audit
AFTER INSERT OR DELETE ON employees
FOR EACH ROW
BEGIN
   INSERT INTO audit_table VALUES (USER, SYSDATE);
END;
```

***

### 8️⃣ Exception Handling

* Predefined Exceptions: NO\_DATA\_FOUND, TOO\_MANY\_ROWS, ZERO\_DIVIDE.
* User-defined:

```
DECLARE
   e_custom EXCEPTION;
BEGIN
   IF v_sal < 0 THEN
      RAISE e_custom;
   END IF;
EXCEPTION
   WHEN e_custom THEN
      DBMS_OUTPUT.PUT_LINE('Salary cannot be negative');
END;
```

* PRAGMA EXCEPTION\_INIT to map Oracle errors.

***

### 9️⃣ Collections

* Associative Arrays (index-by tables)
* Nested Tables
* VARRAYs

```
TYPE name_tab IS TABLE OF VARCHAR2(50);
v_names name_tab := name_tab();
```

Use BULK COLLECT & FORALL for bulk operations.

***

### 🔟 Performance & Optimization

* Use BULK COLLECT and FORALL for large DML.
* Bind variables to avoid hard parsing.
* Use LIMIT in bulk fetch.
* Proper indexing, EXPLAIN PLAN for query tuning.

***

### 11️⃣ Dynamic SQL

* EXECUTE IMMEDIATE for DDL or dynamic queries.

```
EXECUTE IMMEDIATE 'CREATE TABLE test(id NUMBER)';
```

* Use bind variables to prevent SQL injection.

***

### 12️⃣ Advanced Topics

*   Autonomous Transactions: Independent commits inside a procedure/trigger.

    PRAGMA AUTONOMOUS\_TRANSACTION.
* Ref Cursors: Strongly or weakly typed cursors returned from procedures.
* Pipelined Table Functions: Return rows as they are produced.
* Materialized Views & DB Links: Often come up in advanced discussions.

***

### 13️⃣ Key Oracle Built-ins

* DBMS\_OUTPUT: Debugging.
* DBMS\_SQL: Dynamic SQL.
* DBMS\_JOB / DBMS\_SCHEDULER: Scheduling jobs.
* DBMS\_ALERT / DBMS\_PIPE: Messaging.

***

### 14️⃣ Interview-Focused Tips

*   Difference SQL vs PL/SQL

    SQL is declarative; PL/SQL adds procedural control.
*   Trigger vs Procedure

    Trigger auto-fires; procedure is invoked explicitly.
*   Exception Propagation

    Unhandled exceptions bubble up to calling block.
*   Transaction Control

    COMMIT, ROLLBACK, SAVEPOINT—understand scope inside procedures/triggers.

***

### 15️⃣ Quick Practice Questions

1. Write a function to return nth highest salary.
2. Create a trigger to log salary changes.
3. Use BULK COLLECT & FORALL to insert 1M rows efficiently.
4. Example of parameterized cursor with dynamic filtering.
5. Demonstrate exception handling for DUP\_VAL\_ON\_INDEX.

***

#### Last-Minute Checklist

* ✅ Understand PL/SQL block structure & scoping rules.
* ✅ Know common predefined exceptions & error codes.
* ✅ Revise differences: Procedure vs Function vs Package vs Trigger.
* ✅ Practice DML with cursors and collections.
* ✅ Review transaction behavior inside triggers.





## Interview questions&#x20;



Here’s a comprehensive PL/SQL Q\&A set—the same 30 interview questions now paired with concise, practical answers.

You can skim key points quickly or elaborate during an interview.

***

### 🟢 Basics & Architecture

<br>

1\. Explain the structure of a PL/SQL block.

* Sections:
  * DECLARE (optional): variables, cursors, constants.
  * BEGIN: executable statements.
  * EXCEPTION (optional): error handling.
  * END;
* Example:

```
DECLARE v_name VARCHAR2(30);
BEGIN
  SELECT first_name INTO v_name FROM employees WHERE employee_id=100;
EXCEPTION
  WHEN NO_DATA_FOUND THEN DBMS_OUTPUT.PUT_LINE('Not found');
END;
```

2\. Difference between SQL and PL/SQL.

* SQL: Declarative, single statements (DML/DDL).
* PL/SQL: Procedural extension of SQL; supports loops, conditions, variables, error handling.

<br>

3\. Anonymous block vs Stored Procedure.

* Anonymous: Not stored in DB; runs once.
* Procedure: Named, compiled, stored for reuse and can have parameters.

<br>

4\. Bind variables and importance.

* Placeholders (:var) whose values are supplied at runtime.
* Reduce parsing overhead and prevent SQL injection.

<br>

5\. Scope and lifetime of variables.

* Scope: Block in which variable is declared.
* Lifetime: Duration of block execution. Nested blocks can shadow outer variables.

***

### 🟠 Data Types & Variables

<br>

6\. %TYPE vs %ROWTYPE.

* %TYPE: Inherits datatype of a column or variable.
* %ROWTYPE: Represents a full row of a table or cursor.

<br>

7\. Record vs Associative Array.

* Record: Single row with multiple fields.
* Associative array: Key-value pairs, index can be integer or string.

<br>

8\. Passing collections to procedures.

* Create a collection TYPE at schema level; use it as parameter:

```
CREATE TYPE num_list IS TABLE OF NUMBER;
CREATE OR REPLACE PROCEDURE p_test(p_ids IN num_list) AS ...
```

***

### 🟡 Control Structures & Cursors

<br>

9\. Implicit vs Explicit cursors.

* Implicit: Automatic for single-row queries/DML.
* Explicit: Declared and controlled by developer for multi-row result sets.

<br>

10\. Parameterized cursor.

```
CURSOR c_emp (p_dept NUMBER) IS
  SELECT empno, ename FROM emp WHERE deptno = p_dept;
```

Call: FOR rec IN c\_emp(10) LOOP … END LOOP;

<br>

11\. Bulk data fetch (BULK COLLECT & FORALL).

* BULK COLLECT retrieves multiple rows into collections in one go.
* FORALL performs bulk DML:

```
FORALL i IN v_ids.FIRST..v_ids.LAST
   UPDATE employees SET salary = salary*1.1 WHERE id = v_ids(i);
```

12\. Cursor attributes.

* %FOUND, %NOTFOUND, %ROWCOUNT, %ISOPEN—return status info about cursor execution.

<br>

13\. Cursor FOR loop vs explicit fetch.

* FOR loop automatically opens, fetches, closes.
* Explicit fetch gives fine-grained control but requires manual open/fetch/close.

***

### 🟢 Procedures, Functions & Packages

<br>

14\. Procedure vs Function.

* Function must return a value; can be used in SELECTs if deterministic.
* Procedure may return via OUT params, cannot be used directly in SQL.

<br>

15\. DML inside a function.

* Allowed if function is called from PL/SQL, not directly from a SELECT (unless it’s autonomous or deterministic with pragma).

<br>

16\. Returning multiple values.

* OUT parameters, collections, or a record as OUT.

<br>

17\. Package advantages.

* Encapsulation, modularity, shared state, easier dependency mgmt.

<br>

18\. Package specification vs body.

* Spec: Public declarations (visible to users).
* Body: Implementation (can hide private code).

<br>

19\. Overloaded procedures/functions.

* Multiple subprograms with same name but different parameter types or counts.

***

### 🟠 Triggers

<br>

20\. BEFORE vs AFTER triggers.

* BEFORE: Fires before DML; good for validation.
* AFTER: Fires after DML; good for logging.

<br>

21\. INSTEAD OF trigger.

* Used on views to perform custom DML logic in place of normal operation.

<br>

22\. Trigger chaining/recursion.

* A trigger can call a procedure that fires another trigger. Recursive firing possible; control with WHEN clauses or disabling triggers.

<br>

23\. Preventing mutating table errors.

* Use statement-level triggers, compound triggers, or autonomous transactions to avoid querying the same table in row-level triggers.

***

### 🟡 Exception Handling

<br>

24\. Predefined exceptions.

* Examples: NO\_DATA\_FOUND, TOO\_MANY\_ROWS, ZERO\_DIVIDE, DUP\_VAL\_ON\_INDEX.

<br>

25\. User-defined exceptions.

```
DECLARE e_sal_low EXCEPTION;
BEGIN
   IF v_sal < 0 THEN RAISE e_sal_low; END IF;
EXCEPTION
   WHEN e_sal_low THEN DBMS_OUTPUT.PUT_LINE('Negative salary');
END;
```

26\. RAISE\_APPLICATION\_ERROR.

* Used to return custom error numbers/messages to the calling environment.
* Syntax: RAISE\_APPLICATION\_ERROR(-20001, 'Custom message');

<br>

27\. RAISE vs RAISE\_APPLICATION\_ERROR.

* RAISE: Propagates an existing or user-defined exception.
* RAISE\_APPLICATION\_ERROR: Creates a new application-specific error with custom message.

***

### 🟢 Performance & Advanced

<br>

28\. Performance tuning tips.

* Use BULK COLLECT/FORALL, avoid unnecessary loops, use bind variables, keep transactions short, analyze execution plans.

<br>

29\. Autonomous transactions.

* Independent transaction within a block or procedure.
* Declared with PRAGMA AUTONOMOUS\_TRANSACTION.
* Useful for logging or auditing without affecting main transaction.

<br>

30\. Dynamic SQL (EXECUTE IMMEDIATE).

* Allows DDL or runtime-constructed statements.
* Example:

```
EXECUTE IMMEDIATE 'CREATE TABLE temp_tab (id NUMBER)';
```

* Use bind variables to avoid SQL injection.

***

#### ✅ Extra Scenario Answers (Short Examples)

* Nth Highest Salary:

```
SELECT MIN(salary)
FROM (SELECT DISTINCT salary FROM employees ORDER BY salary DESC)
WHERE ROWNUM <= :n;
```

* Audit Trigger:

```
CREATE OR REPLACE TRIGGER emp_audit
AFTER UPDATE ON employees
FOR EACH ROW
BEGIN
  INSERT INTO audit_log(emp_id, old_sal, new_sal, changed_on)
  VALUES (:OLD.emp_id, :OLD.salary, :NEW.salary, SYSDATE);
END;
```

***

This set covers definitions, best practices, and code snippets—enough for most PL/SQL interviews.

Would you like me to convert this Q\&A into a printable PDF cheat sheet for easier last-minute revision?



## Coding questions --



Below is a complete PL/SQL coding-practice pack: the 30 questions from before, now each with a working example answer (all runnable on an Oracle database).

Each answer is deliberately concise so you can copy-paste and test.

***

### 🟢 Beginner

<br>

1\. Hello PL/SQL

```
BEGIN
  DBMS_OUTPUT.PUT_LINE('Hello World');
END;
```

2\. Sum/Difference/Product/Quotient

```
DECLARE
  a NUMBER := 10; b NUMBER := 5;
BEGIN
  DBMS_OUTPUT.PUT_LINE('Sum='||(a+b));
  DBMS_OUTPUT.PUT_LINE('Diff='||(a-b));
  DBMS_OUTPUT.PUT_LINE('Prod='||(a*b));
  DBMS_OUTPUT.PUT_LINE('Quot='||(a/b));
END;
```

3\. Odd/Even Check

```
DECLARE n NUMBER := &num;
BEGIN
  IF MOD(n,2)=0 THEN
    DBMS_OUTPUT.PUT_LINE('Even');
  ELSE
    DBMS_OUTPUT.PUT_LINE('Odd');
  END IF;
END;
```

4\. Fibonacci (first 10)

```
DECLARE a NUMBER := 0; b NUMBER := 1; c NUMBER;
BEGIN
  DBMS_OUTPUT.PUT_LINE(a); DBMS_OUTPUT.PUT_LINE(b);
  FOR i IN 3..10 LOOP
    c := a + b; DBMS_OUTPUT.PUT_LINE(c);
    a := b; b := c;
  END LOOP;
END;
```

5\. SELECT INTO

```
DECLARE v_name employees.first_name%TYPE;
BEGIN
  SELECT first_name INTO v_name FROM employees WHERE employee_id = &id;
  DBMS_OUTPUT.PUT_LINE('Name: '||v_name);
END;
```

***

### 🟠 Intermediate

<br>

6\. Explicit Cursor

```
DECLARE
  CURSOR c IS SELECT first_name, salary FROM employees WHERE department_id = &dept;
  v_name employees.first_name%TYPE; v_sal employees.salary%TYPE;
BEGIN
  OPEN c;
  LOOP
    FETCH c INTO v_name, v_sal;
    EXIT WHEN c%NOTFOUND;
    DBMS_OUTPUT.PUT_LINE(v_name||' earns '||v_sal);
  END LOOP;
  CLOSE c;
END;
```

7\. Parameterized Cursor

```
DECLARE
  CURSOR c(p_sal NUMBER) IS SELECT first_name FROM employees WHERE salary > p_sal;
BEGIN
  FOR r IN c(&salary) LOOP
    DBMS_OUTPUT.PUT_LINE(r.first_name);
  END LOOP;
END;
```

8\. Factorial Function

```
CREATE OR REPLACE FUNCTION factorial(n NUMBER) RETURN NUMBER IS
  res NUMBER := 1;
BEGIN
  FOR i IN 1..n LOOP res := res*i; END LOOP;
  RETURN res;
END;
```

9\. Procedure – Update Salary

```
CREATE OR REPLACE PROCEDURE raise_salary(p_id NUMBER, p_pct NUMBER) AS
BEGIN
  UPDATE employees SET salary = salary*(1 + p_pct/100) WHERE employee_id = p_id;
END;
```

10\. Overloaded Procedure

```
CREATE OR REPLACE PACKAGE p_raise AS
  PROCEDURE raise_emp(p_id NUMBER, p_pct NUMBER);
  PROCEDURE raise_dept(p_dept NUMBER, p_pct NUMBER);
END;
/
CREATE OR REPLACE PACKAGE BODY p_raise AS
  PROCEDURE raise_emp(p_id NUMBER, p_pct NUMBER) IS
  BEGIN UPDATE employees SET salary=salary*(1+p_pct/100) WHERE employee_id=p_id; END;
  PROCEDURE raise_dept(p_dept NUMBER, p_pct NUMBER) IS
  BEGIN UPDATE employees SET salary=salary*(1+p_pct/100) WHERE department_id=p_dept; END;
END;
/
```

11\. Min & Max Salary OUT Params

```
CREATE OR REPLACE PROCEDURE min_max_sal(p_min OUT NUMBER, p_max OUT NUMBER) AS
BEGIN
  SELECT MIN(salary), MAX(salary) INTO p_min, p_max FROM employees;
END;
```

12\. Simple Package

```
CREATE OR REPLACE PACKAGE log_pkg AS
  PROCEDURE add_log(msg VARCHAR2);
  PROCEDURE show_logs;
END;
/
CREATE OR REPLACE PACKAGE BODY log_pkg AS
  PROCEDURE add_log(msg VARCHAR2) IS
  BEGIN INSERT INTO log_table(text,log_time) VALUES (msg,SYSDATE); END;
  PROCEDURE show_logs IS
  BEGIN FOR r IN (SELECT * FROM log_table) LOOP DBMS_OUTPUT.PUT_LINE(r.text); END LOOP; END;
END;
/
```

***

### 🟡 Collections & Bulk

<br>

13\. Bulk Collect

```
DECLARE
  TYPE id_tab IS TABLE OF employees.employee_id%TYPE;
  v_ids id_tab;
BEGIN
  SELECT employee_id BULK COLLECT INTO v_ids FROM employees;
  FOR i IN 1..v_ids.COUNT LOOP DBMS_OUTPUT.PUT_LINE(v_ids(i)); END LOOP;
END;
```

14\. FORALL Bulk Update

```
CREATE OR REPLACE PROCEDURE inc_salary(ids SYS.ODCINUMBERLIST) IS
BEGIN
  FORALL i IN INDICES OF ids
    UPDATE employees SET salary = salary * 1.05 WHERE employee_id = ids(i);
END;
```

15\. Associative Array Sum

```
DECLARE
  TYPE price_tab IS TABLE OF NUMBER INDEX BY VARCHAR2(20);
  items price_tab; total NUMBER := 0;
BEGIN
  items('A'):=10; items('B'):=15;
  FOR i IN items.FIRST .. items.LAST LOOP
    total := total + items(i);
  END LOOP;
  DBMS_OUTPUT.PUT_LINE('Total='||total);
END;
```

16\. Remove Duplicates from Nested Table

```
DECLARE
  TYPE num_tab IS TABLE OF NUMBER;
  t num_tab := num_tab(1,2,2,3,3,4);
BEGIN
  SELECT DISTINCT COLUMN_VALUE BULK COLLECT INTO t FROM TABLE(t);
  FOR i IN 1..t.COUNT LOOP DBMS_OUTPUT.PUT_LINE(t(i)); END LOOP;
END;
```

***

### 🟢 Triggers & Exceptions

<br>

17\. Audit Trigger

```
CREATE OR REPLACE TRIGGER trg_audit
AFTER UPDATE OF salary ON employees
FOR EACH ROW
BEGIN
  INSERT INTO audit_log(emp_id, old_sal, new_sal, changed_on)
  VALUES(:OLD.employee_id, :OLD.salary, :NEW.salary, SYSDATE);
END;
```

18\. Prevent Deletion During Business Hours

```
CREATE OR REPLACE TRIGGER trg_no_del
BEFORE DELETE ON critical_table
BEGIN
  IF TO_CHAR(SYSDATE,'HH24') BETWEEN '09' AND '18' THEN
    RAISE_APPLICATION_ERROR(-20001,'Deletion not allowed in business hours');
  END IF;
END;
```

19\. INSTEAD OF Trigger on View

```
CREATE OR REPLACE TRIGGER trg_view_insert
INSTEAD OF INSERT ON emp_dept_view
FOR EACH ROW
BEGIN
  INSERT INTO employees(employee_id,first_name,department_id)
  VALUES(:NEW.employee_id,:NEW.first_name,:NEW.department_id);
END;
```

20\. Custom Exception

```
DECLARE
  e_neg_sal EXCEPTION;
BEGIN
  IF &sal < 0 THEN RAISE e_neg_sal; END IF;
EXCEPTION
  WHEN e_neg_sal THEN DBMS_OUTPUT.PUT_LINE('Salary cannot be negative');
END;
```

21\. RAISE\_APPLICATION\_ERROR

```
CREATE OR REPLACE TRIGGER trg_join_date
BEFORE INSERT ON employees
FOR EACH ROW
BEGIN
  IF :NEW.hire_date < SYSDATE THEN
    RAISE_APPLICATION_ERROR(-20002,'Hire date cannot be in past');
  END IF;
END;
```

***

### 🟠 Advanced SQL / PL/SQL

<br>

22\. Nth Highest Salary

```
CREATE OR REPLACE FUNCTION nth_highest(n NUMBER) RETURN NUMBER IS
  sal NUMBER;
BEGIN
  SELECT MIN(salary) INTO sal
  FROM (SELECT DISTINCT salary FROM employees ORDER BY salary DESC)
  WHERE ROWNUM <= n;
  RETURN sal;
END;
```

23\. Palindrome Check

```
CREATE OR REPLACE FUNCTION is_palindrome(p_str VARCHAR2) RETURN VARCHAR2 IS
BEGIN
  IF REVERSE(p_str) = p_str THEN RETURN 'YES'; ELSE RETURN 'NO'; END IF;
END;
```

24\. Prime Numbers Between Two Values

```
CREATE OR REPLACE PROCEDURE primes(a NUMBER, b NUMBER) AS
  flag BOOLEAN;
BEGIN
  FOR i IN a..b LOOP
    flag := TRUE;
    FOR j IN 2..TRUNC(SQRT(i)) LOOP
      IF MOD(i,j)=0 THEN flag := FALSE; EXIT; END IF;
    END LOOP;
    IF flag AND i>1 THEN DBMS_OUTPUT.PUT_LINE(i); END IF;
  END LOOP;
END;
```

25\. Dynamic Table Creation

```
CREATE OR REPLACE PROCEDURE create_tab(p_name VARCHAR2) AS
BEGIN
  EXECUTE IMMEDIATE 'CREATE TABLE '||p_name||'(id NUMBER)';
END;
```

26\. Dynamic SELECT

```
CREATE OR REPLACE PROCEDURE dyn_query(p_col VARCHAR2,p_val VARCHAR2) AS
  v_sql VARCHAR2(200);
  v_res VARCHAR2(100);
BEGIN
  v_sql := 'SELECT '||p_col||' FROM employees WHERE '||p_col||'=:x';
  EXECUTE IMMEDIATE v_sql INTO v_res USING p_val;
  DBMS_OUTPUT.PUT_LINE('Result: '||v_res);
END;
```

***

### 🟡 Real-World Scenarios

<br>

27\. Pagination Rows N to M

```
CREATE OR REPLACE PROCEDURE fetch_range(p_from NUMBER, p_to NUMBER) AS
BEGIN
  FOR r IN (SELECT * FROM (
              SELECT e.*, ROW_NUMBER() OVER (ORDER BY employee_id) rn FROM employees e
            ) WHERE rn BETWEEN p_from AND p_to) LOOP
    DBMS_OUTPUT.PUT_LINE(r.employee_id||' '||r.first_name);
  END LOOP;
END;
```

28\. Error Logging with Autonomous Txn

```
CREATE OR REPLACE PROCEDURE log_error(p_msg VARCHAR2) IS
  PRAGMA AUTONOMOUS_TRANSACTION;
BEGIN
  INSERT INTO error_log(msg,log_time) VALUES (p_msg,SYSDATE);
  COMMIT;
END;
```

29\. Monthly Sales Summary

```
CREATE OR REPLACE PROCEDURE monthly_summary IS
BEGIN
  INSERT INTO sales_summary(product_id, month_start, total_amt)
  SELECT product_id, TRUNC(ADD_MONTHS(SYSDATE,-1),'MM'),
         SUM(amount)
  FROM sales
  WHERE TRUNC(sale_date,'MM') = TRUNC(ADD_MONTHS(SYSDATE,-1),'MM')
  GROUP BY product_id;
END;
```

30\. Employee Hierarchy Tree

```
CREATE OR REPLACE PROCEDURE show_hierarchy(p_mgr NUMBER) AS
BEGIN
  FOR r IN (
    SELECT employee_id, first_name, level
    FROM employees
    START WITH manager_id = p_mgr
    CONNECT BY PRIOR employee_id = manager_id
  ) LOOP
    DBMS_OUTPUT.PUT_LINE(LPAD(' ', (r.level-1)*2)||r.first_name);
  END LOOP;
END;
```

***

#### Usage Notes

* All examples assume common Oracle sample tables (employees, etc.).
* Replace & variables or SYS.ODCINUMBERLIST with your test data when running.
* Add proper exception handling or commit/rollback statements in production.

<br>

These question-answer pairs cover the spectrum—procedures, functions, triggers, collections, dynamic SQL, and performance tuning—perfect for interview preparation and practice.
