import PageLayout from "../layouts/PageLayout";
import React, { useState, useEffect } from 'react';
import { Card, CardBody, CardHeader, Typography, Button, Alert, Spinner, Chip, Dialog, DialogHeader, DialogBody, DialogFooter, Textarea } from '@material-tailwind/react';
import { useAuth, api } from '../contexts/AuthContext';

const SuperAdminApprovals = () => {
  const { user: authUser } = useAuth();
  const [requests, setRequests] = useState([]);
  const [loading, setLoading] = useState(true);
  const [processing, setProcessing] = useState(null);
  const [alert, setAlert] = useState({ show: false, message: '', type: 'success' });
  const [selectedRequest, setSelectedRequest] = useState(null);
  const [reviewComment, setReviewComment] = useState('');
  const [showReviewDialog, setShowReviewDialog] = useState(false);

  useEffect(() => {
    fetchRequests();
  }, []);

  const fetchRequests = async () => {
    try {
      setLoading(true);
      const response = await api.get('/profile/requests');
      setRequests(response.data);
    } catch (error) {
      console.error('Error fetching requests:', error);
      setAlert({ show: true, message: 'Failed to load requests. Please try again.', type: 'error' });
    } finally {
      setLoading(false);
    }
  };

  const handleApprove = async (requestId) => {
    try {
      setProcessing(requestId);
      await api.post(`/profile/approve/${requestId}`, {
        review_comment: reviewComment
      });
      setAlert({ show: true, message: 'Request approved successfully!', type: 'success' });
      fetchRequests();
      setShowReviewDialog(false);
      setSelectedRequest(null);
      setReviewComment('');
    } catch (error) {
      console.error('Error approving request:', error);
      setAlert({ show: true, message: 'Failed to approve request. Please try again.', type: 'error' });
    } finally {
      setProcessing(null);
    }
  };

  const handleReject = async (requestId) => {
    try {
      setProcessing(requestId);
      await api.post(`/profile/reject/${requestId}`, {
        review_comment: reviewComment
      });
      setAlert({ show: true, message: 'Request rejected.', type: 'success' });
      fetchRequests();
      setShowReviewDialog(false);
      setSelectedRequest(null);
      setReviewComment('');
    } catch (error) {
      console.error('Error rejecting request:', error);
      setAlert({ show: true, message: 'Failed to reject request. Please try again.', type: 'error' });
    } finally {
      setProcessing(null);
    }
  };

  const openReviewDialog = (request, action) => {
    setSelectedRequest({ ...request, action });
    setShowReviewDialog(true);
  };

  const getStatusColor = (status) => {
    switch (status) {
      case 'pending': return 'orange';
      case 'approved': return 'green';
      case 'rejected': return 'red';
      default: return 'gray';
    }
  };

  const formatPayload = (payload) => {
    if (!payload) return 'No changes requested';
    return Object.entries(payload)
      .map(([key, value]) => `${key}: ${value || 'Not set'}`)
      .join(', ');
  };

  if (loading) {
    return (
      <PageLayout>
        <div className="flex justify-center items-center h-64">
          <Spinner className="h-8 w-8" />
        </div>
      </PageLayout>
    );
  }

  return (
    <PageLayout>
      <div className="p-4">
        <Typography variant="h3" color="blue-gray" className="mb-6">
          Profile Update Requests
        </Typography>

        {alert.show && (
          <Alert color={alert.type === 'success' ? 'green' : 'red'} className="mb-6">
            {alert.message}
          </Alert>
        )}

        <div className="space-y-4">
          {requests.length === 0 ? (
            <Card>
              <CardBody>
                <Typography variant="h6" color="gray">
                  No pending requests
                </Typography>
              </CardBody>
            </Card>
          ) : (
            requests.map((request) => (
              <Card key={request.id}>
                <CardHeader floated={false} shadow={false} color="transparent">
                  <div className="flex justify-between items-center">
                    <Typography variant="h6" color="blue-gray">
                      Request #{request.id} - {request.user.full_name}
                    </Typography>
                    <Chip color={getStatusColor(request.status)} value={request.status} />
                  </div>
                </CardHeader>
                <CardBody>
                  <div className="grid grid-cols-1 md:grid-cols-2 gap-4 mb-4">
                    <div>
                      <Typography variant="small" color="gray" className="font-medium">
                        Requested Changes
                      </Typography>
                      <Typography variant="body2" color="blue-gray">
                        {formatPayload(request.payload)}
                      </Typography>
                    </div>
                    <div>
                      <Typography variant="small" color="gray" className="font-medium">
                        Requested At
                      </Typography>
                      <Typography variant="body2" color="blue-gray">
                        {new Date(request.created_at).toLocaleString()}
                      </Typography>
                    </div>
                  </div>

                  {request.review_comment && (
                    <div className="mb-4">
                      <Typography variant="small" color="gray" className="font-medium">
                        Review Comment
                      </Typography>
                      <Typography variant="body2" color="blue-gray">
                        {request.review_comment}
                      </Typography>
                    </div>
                  )}

                  {request.status === 'pending' && (
                    <div className="flex gap-2">
                      <Button
                        size="sm"
                        color="green"
                        onClick={() => openReviewDialog(request, 'approve')}
                        loading={processing === request.id}
                        disabled={processing === request.id}
                      >
                        Approve
                      </Button>
                      <Button
                        size="sm"
                        color="red"
                        variant="outlined"
                        onClick={() => openReviewDialog(request, 'reject')}
                        loading={processing === request.id}
                        disabled={processing === request.id}
                      >
                        Reject
                      </Button>
                    </div>
                  )}
                </CardBody>
              </Card>
            ))
          )}
        </div>

        {/* Review Dialog */}
        <Dialog open={showReviewDialog} handler={setShowReviewDialog}>
          <DialogHeader>
            {selectedRequest?.action === 'approve' ? 'Approve' : 'Reject'} Request
          </DialogHeader>
          <DialogBody>
            <Typography variant="body1" color="blue-gray" className="mb-4">
              {selectedRequest?.action === 'approve' ? 'Approve' : 'Reject'} the profile update request for {selectedRequest?.user?.full_name}?
            </Typography>
            <div>
              <Typography variant="small" color="blue-gray" className="mb-2 font-medium">
                Review Comment (Optional)
              </Typography>
              <Textarea
                value={reviewComment}
                onChange={(e) => setReviewComment(e.target.value)}
                placeholder="Add a comment about your decision..."
              />
            </div>
          </DialogBody>
          <DialogFooter>
            <Button
              variant="text"
              color="gray"
              onClick={() => setShowReviewDialog(false)}
            >
              Cancel
            </Button>
            <Button
              color={selectedRequest?.action === 'approve' ? 'green' : 'red'}
              onClick={() => {
                if (selectedRequest?.action === 'approve') {
                  handleApprove(selectedRequest.id);
                } else {
                  handleReject(selectedRequest.id);
                }
              }}
              loading={processing === selectedRequest?.id}
            >
              {selectedRequest?.action === 'approve' ? 'Approve' : 'Reject'}
            </Button>
          </DialogFooter>
        </Dialog>
      </div>
    </PageLayout>
  );
};

export default SuperAdminApprovals;
