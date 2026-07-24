# Fix: Stron Vending Returns Empty List Instead of Token ✅

## Issue
Error: `Vending failed: Stron did not return a token: []`
- Stron API returns HTTP 200 with empty list `[]` instead of a token object
- `_raise_for_api_error` silently ignored non-dict responses (like lists)
- Error message was unhelpful for debugging

## Completed

- [x] Step 0: Read all relevant files and understand the codebase
- [x] Step 1: Plan approved by user
- [x] Step 2: Edit `backend/apps/tokens/services/stron.py`:
  - [x] 2a. Fix `_raise_for_api_error` to handle list/empty/unexpected responses
  - [x] 2b. Update `_parse_vending_response` with better validation and error messages
  - [x] 2c. Add structured logging in `_post` for debugging (safe payload logging)
  - [x] 2d. Add structured logging in `_parse_vending_response` (success + failure)
  - [x] 2e. Fix Amount field type per v5.0.0 manual:
       - VendingMeter: Amount must be number (100), not string ("100")
       - VendingMeterDirectly: Amount must be string ("30") 
       - VendingMeterPreview: Amount must be number
- [x] Step 3: Update tests to match new Amount types
- [x] Step 4: Run tests — all 6 token service tests pass ✅


