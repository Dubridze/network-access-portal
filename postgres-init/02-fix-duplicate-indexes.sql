-- Script to fix duplicate index names in the database
-- This script renames existing indexes to match the new naming convention
-- to prevent DuplicateTable errors

-- Drop old indexes (they will be recreated by SQLAlchemy with new names)
DO $$
BEGIN
  -- Drop duplicate idx_created_at if it exists in access_requests
  IF EXISTS (
    SELECT 1 FROM information_schema.tables 
    WHERE table_name = 'access_requests' 
    AND table_schema = 'public'
  ) THEN
    -- First check if the problematic indexes exist
    EXECUTE 'DROP INDEX IF EXISTS idx_created_at CASCADE';
    EXECUTE 'DROP INDEX IF EXISTS idx_user_id CASCADE';
    EXECUTE 'DROP INDEX IF EXISTS idx_status CASCADE';
    EXECUTE 'DROP INDEX IF EXISTS idx_approver_id CASCADE';
    EXECUTE 'DROP INDEX IF EXISTS idx_access_request_id CASCADE';
    EXECUTE 'DROP INDEX IF EXISTS idx_action CASCADE';
    EXECUTE 'DROP INDEX IF EXISTS idx_key CASCADE';
  END IF;
END
$$;

-- Note: New indexes with table-specific prefixes will be created automatically
-- by SQLAlchemy on the next application startup with the updated models.py
