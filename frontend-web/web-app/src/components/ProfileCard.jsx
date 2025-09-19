import React from 'react';
import { Card, CardBody, Avatar, Typography, Button } from '@material-tailwind/react';

const ProfileCard = ({ user, onEdit }) => {
  if (!user) return <div>Loading profile...</div>;

  return (
    <Card className="w-full max-w-sm">
      <CardBody className="text-center">
        <Avatar
          src={user.profile_picture_url || 'https://via.placeholder.com/150'}
          alt={user.full_name}
          size="xl"
          className="mx-auto mb-4"
        />
        <Typography variant="h5" color="blue-gray" className="mb-2">
          {user.full_name}
        </Typography>
        <Typography variant="small" color="gray" className="mb-2">
          {user.role}
        </Typography>
        <Typography variant="small" color="gray" className="mb-4">
          Employee ID: {user.employee_id || 'Not set'}
        </Typography>
        <Button onClick={onEdit} className="w-full">
          Edit Profile
        </Button>
      </CardBody>
    </Card>
  );
};

export default ProfileCard;
