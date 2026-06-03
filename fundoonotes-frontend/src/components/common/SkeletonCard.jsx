import React from 'react';
import Card from '@mui/material/Card';
import CardContent from '@mui/material/CardContent';
import Skeleton from '@mui/material/Skeleton';

export default function SkeletonCard() {
  return (
    <Card sx={{ mb: 2, borderRadius: 2 }}>
      <CardContent>
        <Skeleton variant="text" width="60%" height={28} />
        <Skeleton variant="text" width="100%" />
        <Skeleton variant="text" width="100%" />
        <Skeleton variant="text" width="80%" />
      </CardContent>
    </Card>
  );
}
