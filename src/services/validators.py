"""Validation services for cluster generation.

This module centralizes all validation logic to avoid duplication
across API routes and ensure consistent validation behavior.
"""

from typing import List
from fastapi import HTTPException, status

from config.constants import Vendor
from models.requests import VendorConfigRequest
from utils.logging import LoggingMixin, get_logger

logger = get_logger(__name__)


class ClusterValidator(LoggingMixin):
    """Centralized validation service for cluster requests."""

    @staticmethod
    def validate_vendors(vendor_configs: List[VendorConfigRequest]) -> None:
        """Validate that all vendor configurations use supported vendors.

        Args:
            vendor_configs: List of vendor configurations to validate.

        Raises:
            HTTPException: If any vendor is not supported.
        """
        valid_vendors = set(Vendor.values())

        for vc in vendor_configs:
            if vc.vendor not in valid_vendors:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail=f"Invalid vendor: {vc.vendor}. Valid vendors: {', '.join(sorted(valid_vendors))}"
                )

    @staticmethod
    def validate_cluster_name(cluster_name: str) -> None:
        """Validate cluster name format.

        Args:
            cluster_name: The cluster name to validate.

        Raises:
            HTTPException: If cluster name is invalid.
        """
        if not cluster_name.islower():
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Cluster name must be lowercase"
            )

        if cluster_name.startswith('-') or cluster_name.endswith('-'):
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Cluster name cannot start or end with hyphen"
            )

        if len(cluster_name) > 63:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Cluster name must be 63 characters or less"
            )
