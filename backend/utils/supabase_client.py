"""
Supabase database wrapper class for common operations.
"""
from typing import Optional, Dict, Any, List
from supabase import Client
from utils.config import get_supabase_client
from utils.exceptions import DatabaseException


class SupabaseDB:
    """Wrapper class for Supabase database operations."""
    
    def __init__(self):
        """Initialize Supabase client."""
        self.client: Client = get_supabase_client()
    
    async def insert(self, table: str, data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Insert a new record into a table.
        
        Args:
            table: Table name
            data: Dictionary of column:value pairs
            
        Returns:
            Inserted record with generated fields
            
        Raises:
            DatabaseException: If insert fails
        """
        try:
            response = self.client.table(table).insert(data).execute()
            if response.data and len(response.data) > 0:
                return response.data[0]
            raise DatabaseException(f"Failed to insert record into {table}")
        except Exception as e:
            if "duplicate" in str(e).lower() or "unique" in str(e).lower():
                raise DatabaseException(f"Duplicate entry in {table}")
            raise DatabaseException(f"Insert failed: {str(e)}")
    
    async def update(self, table: str, record_id: str, data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Update a record in a table by ID.
        
        Args:
            table: Table name
            record_id: Record UUID
            data: Dictionary of fields to update
            
        Returns:
            Updated record
            
        Raises:
            DatabaseException: If update fails
        """
        try:
            response = self.client.table(table).update(data).eq('id', record_id).execute()
            if response.data and len(response.data) > 0:
                return response.data[0]
            raise DatabaseException(f"Record with id '{record_id}' not found in {table}")
        except Exception as e:
            raise DatabaseException(f"Update failed: {str(e)}")
    
    async def delete(self, table: str, record_id: str) -> bool:
        """
        Delete a record from a table by ID.
        
        Args:
            table: Table name
            record_id: Record UUID
            
        Returns:
            True if deleted successfully
            
        Raises:
            DatabaseException: If delete fails
        """
        try:
            response = self.client.table(table).delete().eq('id', record_id).execute()
            return True
        except Exception as e:
            raise DatabaseException(f"Delete failed: {str(e)}")
    
    async def select(self, table: str, columns: str = "*") -> List[Dict[str, Any]]:
        """
        Select all records from a table.
        
        Args:
            table: Table name
            columns: Columns to select (default: all)
            
        Returns:
            List of records
            
        Raises:
            DatabaseException: If select fails
        """
        try:
            response = self.client.table(table).select(columns).execute()
            return response.data if response.data else []
        except Exception as e:
            raise DatabaseException(f"Select failed: {str(e)}")
    
    async def select_by_id(self, table: str, record_id: str, columns: str = "*") -> Optional[Dict[str, Any]]:
        """
        Select a single record by ID.
        
        Args:
            table: Table name
            record_id: Record UUID
            columns: Columns to select (default: all)
            
        Returns:
            Record dictionary or None if not found
            
        Raises:
            DatabaseException: If select fails
        """
        try:
            response = self.client.table(table).select(columns).eq('id', record_id).execute()
            if response.data and len(response.data) > 0:
                return response.data[0]
            return None
        except Exception as e:
            raise DatabaseException(f"Select by ID failed: {str(e)}")
    
    async def select_where(
        self, 
        table: str, 
        column: str, 
        value: Any, 
        columns: str = "*"
    ) -> List[Dict[str, Any]]:
        """
        Select records where column equals value.
        
        Args:
            table: Table name
            column: Column name to filter
            value: Value to match
            columns: Columns to select (default: all)
            
        Returns:
            List of matching records
            
        Raises:
            DatabaseException: If select fails
        """
        try:
            response = self.client.table(table).select(columns).eq(column, value).execute()
            return response.data if response.data else []
        except Exception as e:
            raise DatabaseException(f"Select where failed: {str(e)}")
    
    async def select_with_filters(
        self,
        table: str,
        filters: Dict[str, Any],
        columns: str = "*",
        order_by: Optional[str] = None,
        ascending: bool = True
    ) -> List[Dict[str, Any]]:
        """
        Select records with multiple filters.
        
        Args:
            table: Table name
            filters: Dictionary of column:value pairs for filtering
            columns: Columns to select (default: all)
            order_by: Column to order by (optional)
            ascending: Sort order (default: True)
            
        Returns:
            List of matching records
            
        Raises:
            DatabaseException: If select fails
        """
        try:
            query = self.client.table(table).select(columns)
            
            # Apply filters
            for column, value in filters.items():
                query = query.eq(column, value)
            
            # Apply ordering
            if order_by:
                query = query.order(order_by, desc=not ascending)
            
            response = query.execute()
            return response.data if response.data else []
        except Exception as e:
            raise DatabaseException(f"Select with filters failed: {str(e)}")
    
    async def count(self, table: str, column: str = "*") -> int:
        """
        Count records in a table.
        
        Args:
            table: Table name
            column: Column to count (default: all)
            
        Returns:
            Number of records
            
        Raises:
            DatabaseException: If count fails
        """
        try:
            response = self.client.table(table).select(column, count="exact").execute()
            return response.count if hasattr(response, 'count') else len(response.data)
        except Exception as e:
            raise DatabaseException(f"Count failed: {str(e)}")
    
    async def exists(self, table: str, column: str, value: Any) -> bool:
        """
        Check if a record exists with the given column value.
        
        Args:
            table: Table name
            column: Column name
            value: Value to check
            
        Returns:
            True if exists, False otherwise
        """
        try:
            response = self.client.table(table).select("id").eq(column, value).limit(1).execute()
            return response.data is not None and len(response.data) > 0
        except Exception:
            return False
    
    async def count_records(self, table: str, where_clause: Optional[Dict[str, Any]] = None) -> int:
        """
        Count records in a table with optional where clause.
        
        Args:
            table: Table name
            where_clause: Dictionary of column:value pairs for filtering
            
        Returns:
            Number of matching records
            
        Raises:
            DatabaseException: If count fails
        """
        try:
            query = self.client.table(table).select("*", count="exact")
            
            # Apply filters if provided
            if where_clause:
                for column, value in where_clause.items():
                    query = query.eq(column, value)
            
            response = query.execute()
            return response.count if hasattr(response, 'count') else len(response.data)
        except Exception as e:
            raise DatabaseException(f"Count records failed: {str(e)}")
    
    async def query_with_aggregation(
        self,
        table: str,
        aggregate_column: str,
        aggregate_function: str = "count",
        group_by: Optional[str] = None,
        where_clause: Optional[Dict[str, Any]] = None
    ) -> List[Dict[str, Any]]:
        """
        Execute an aggregation query.
        
        Note: Supabase doesn't directly support GROUP BY in the client library.
        This method fetches data and performs aggregation in Python.
        
        Args:
            table: Table name
            aggregate_column: Column to aggregate
            aggregate_function: Function to apply (count, sum, avg, etc.)
            group_by: Column to group by
            where_clause: Optional filtering
            
        Returns:
            List of aggregated results
            
        Raises:
            DatabaseException: If query fails
        """
        try:
            # Fetch data with filters
            query = self.client.table(table).select("*")
            
            if where_clause:
                for column, value in where_clause.items():
                    query = query.eq(column, value)
            
            response = query.execute()
            data = response.data if response.data else []
            
            # Perform aggregation in Python
            if not group_by:
                # Simple aggregation without grouping
                if aggregate_function == "count":
                    return [{"count": len(data)}]
                elif aggregate_function == "sum" and aggregate_column:
                    total = sum(row.get(aggregate_column, 0) for row in data)
                    return [{"sum": total}]
                elif aggregate_function == "avg" and aggregate_column:
                    values = [row.get(aggregate_column, 0) for row in data]
                    avg = sum(values) / len(values) if values else 0
                    return [{"avg": avg}]
            else:
                # Group by aggregation
                from collections import defaultdict
                groups = defaultdict(list)
                
                for row in data:
                    key = row.get(group_by)
                    groups[key].append(row)
                
                results = []
                for key, rows in groups.items():
                    result = {group_by: key}
                    
                    if aggregate_function == "count":
                        result["count"] = len(rows)
                    elif aggregate_function == "sum" and aggregate_column:
                        result["sum"] = sum(r.get(aggregate_column, 0) for r in rows)
                    elif aggregate_function == "avg" and aggregate_column:
                        values = [r.get(aggregate_column, 0) for r in rows]
                        result["avg"] = sum(values) / len(values) if values else 0
                    
                    results.append(result)
                
                return results
            
            return []
        except Exception as e:
            raise DatabaseException(f"Aggregation query failed: {str(e)}")
    
    async def select_with_join(
        self,
        main_table: str,
        join_table: str,
        join_condition: str,
        select_columns: str = "*"
    ) -> List[Dict[str, Any]]:
        """
        Select data with a join (using Supabase's foreign key relationships).
        
        Note: Supabase uses foreign key relationships for joins.
        This method uses the embedded resource syntax.
        
        Args:
            main_table: Main table name
            join_table: Table to join with
            join_condition: Foreign key column (e.g., "project_id")
            select_columns: Columns to select
            
        Returns:
            List of joined records
            
        Raises:
            DatabaseException: If join fails
        """
        try:
            # Use Supabase's embedded resource syntax
            # Example: select="*, projects(*)" to get related project data
            select_str = f"{select_columns}, {join_table}(*)"
            
            response = self.client.table(main_table).select(select_str).execute()
            return response.data if response.data else []
        except Exception as e:
            raise DatabaseException(f"Join query failed: {str(e)}")
    
    async def custom_query(self, query_func) -> Any:
        """
        Execute a custom query function.
        
        Args:
            query_func: Function that takes the client and returns a query
            
        Returns:
            Query result
            
        Raises:
            DatabaseException: If query fails
        """
        try:
            result = query_func(self.client)
            return result
        except Exception as e:
            raise DatabaseException(f"Custom query failed: {str(e)}")


# Global instance
_db_instance: Optional[SupabaseDB] = None


def get_db() -> SupabaseDB:
    """
    Get the global SupabaseDB instance.
    
    Returns:
        SupabaseDB instance
    """
    global _db_instance
    if _db_instance is None:
        _db_instance = SupabaseDB()
    return _db_instance

