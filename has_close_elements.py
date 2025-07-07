from typing import List


def has_close_elements(numbers: List[float], threshold: float) -> bool:
    """
    Check whether in given list of numbers, are any two numbers closer to each other than
    given threshold.
    
    Args:
        numbers: List of float numbers
        threshold: Minimum distance threshold
        
    Returns:
        True if any two numbers are closer than threshold, False otherwise
        
    Examples:
        >>> has_close_elements([1.0, 2.0, 3.0], 0.5)
        False
        >>> has_close_elements([1.0, 2.8, 3.0, 4.0, 5.0, 2.0], 0.3)
        True
    """
    # Compare each pair of numbers
    for i in range(len(numbers)):
        for j in range(i + 1, len(numbers)):
            # Calculate absolute difference
            distance = abs(numbers[i] - numbers[j])
            # If distance is less than threshold, return True
            if distance < threshold:
                return True
    
    # No close elements found
    return False


# Test cases
if __name__ == "__main__":
    # Test case 1: No close elements
    assert has_close_elements([1.0, 2.0, 3.0], 0.5) == False
    
    # Test case 2: Has close elements
    assert has_close_elements([1.0, 2.8, 3.0, 4.0, 5.0, 2.0], 0.3) == True
    
    # Test case 3: Empty list
    assert has_close_elements([], 1.0) == False
    
    # Test case 4: Single element
    assert has_close_elements([1.0], 0.1) == False
    
    # Test case 5: Identical elements
    assert has_close_elements([1.0, 1.0], 0.1) == True
    
    # Test case 6: Edge case with threshold 0
    assert has_close_elements([1.0, 2.0], 0.0) == False
    assert has_close_elements([1.0, 1.0], 0.0) == False  # Distance is 0, not < 0
    
    print("✅ All test cases passed!")
