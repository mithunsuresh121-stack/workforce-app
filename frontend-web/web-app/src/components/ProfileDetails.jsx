import React from 'react';
import { Typography, Card, CardBody } from '@material-tailwind/react';

const ProfileDetails = ({ profile }) => {
  if (!profile) {
    return (
      <Card>
        <CardBody>
          <Typography variant="h6" color="gray">
            Profile details not available
          </Typography>
        </CardBody>
      </Card>
    );
  }

  return (
    <Card>
      <CardBody>
        <Typography variant="h5" color="blue-gray" className="mb-4">
          Profile Details
        </Typography>
        <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
          <div>
            <Typography variant="small" color="gray" className="font-medium">
              Department
            </Typography>
            <Typography variant="body1" color="blue-gray">
              {profile.department || 'Not set'}
            </Typography>
          </div>
          <div>
            <Typography variant="small" color="gray" className="font-medium">
              Position
            </Typography>
            <Typography variant="body1" color="blue-gray">
              {profile.position || 'Not set'}
            </Typography>
          </div>
          <div>
            <Typography variant="small" color="gray" className="font-medium">
              Phone
            </Typography>
            <Typography variant="body1" color="blue-gray">
              {profile.phone || 'Not set'}
            </Typography>
          </div>
          <div>
            <Typography variant="small" color="gray" className="font-medium">
              Hire Date
            </Typography>
            <Typography variant="body1" color="blue-gray">
              {profile.hire_date ? new Date(profile.hire_date).toLocaleDateString() : 'Not set'}
            </Typography>
          </div>
          <div>
            <Typography variant="small" color="gray" className="font-medium">
              Gender
            </Typography>
            <Typography variant="body1" color="blue-gray">
              {profile.gender || 'Not set'}
            </Typography>
          </div>
          <div>
            <Typography variant="small" color="gray" className="font-medium">
              Address
            </Typography>
            <Typography variant="body1" color="blue-gray">
              {profile.address || 'Not set'}
            </Typography>
          </div>
          <div>
            <Typography variant="small" color="gray" className="font-medium">
              City
            </Typography>
            <Typography variant="body1" color="blue-gray">
              {profile.city || 'Not set'}
            </Typography>
          </div>
          <div>
            <Typography variant="small" color="gray" className="font-medium">
              Emergency Contact
            </Typography>
            <Typography variant="body1" color="blue-gray">
              {profile.emergency_contact || 'Not set'}
            </Typography>
          </div>
        </div>
      </CardBody>
    </Card>
  );
};

export default ProfileDetails;
