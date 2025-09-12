from typing import Dict, List, Optional
import weakref
from collections import defaultdict

from core.simulation.event_bus.base_event import BaseEvent

class EventBus:
    """Central event bus for decoupled communication"""
    
    def __init__(self):
        # Original broadcast subscribers
        self._subscribers: Dict[type, List[weakref.ReferenceType]] = defaultdict(list)
        # Targeted subscribers: {event_type: {receiver_id: [handlers]}}
        self._receiver_subscribers: Dict[type, Dict[str, List[weakref.ReferenceType]]] = defaultdict(lambda: defaultdict(list))
        
    def subscribe(self, event_type: type, handler_method, receiver_id: Optional[str] = None) -> None:
        """
        Subscribe to events of a specific type
        
        Args:
            event_type: The type of event to subscribe to
            handler_method: The method to call when event occurs
            receiver_id: If provided, only receive events targeted to this receiver
        """
        # Create weak reference to prevent circular references
        if hasattr(handler_method, '__self__'):
            # Method is bound to an instance
            obj_ref = weakref.ref(handler_method.__self__)
            method_name = handler_method.__name__
            weak_handler = lambda event: self._call_weak_method(obj_ref, method_name, event)
        else:
            # Function or static method
            weak_handler = weakref.ref(handler_method)
            
        weak_ref = weakref.ref(weak_handler)
        
        if receiver_id is None:
            # Subscribe to all events of this type (broadcast)
            self._subscribers[event_type].append(weak_ref)
        else:
            # Subscribe only to events targeted at specific receiver
            self._receiver_subscribers[event_type][receiver_id].append(weak_ref)
        
    def _call_weak_method(self, obj_ref, method_name, event):
        """Safely call method on weakly referenced object"""
        obj = obj_ref()
        if obj is not None:
            method = getattr(obj, method_name, None)
            if method:
                method(event)
                
    def publish(self, event: BaseEvent) -> None:
        """Publish an event to appropriate subscribers"""
        event_type = type(event)
        
        # Check if this event has a specific receiver
        receiver_id = getattr(event, 'receiver', None)
        
        if receiver_id:
            # Targeted message - only send to specific receiver subscribers
            self._publish_to_receiver(event, event_type, receiver_id)
        else:
            # Broadcast message - send to all general subscribers
            self._publish_broadcast(event, event_type)
    
    def _publish_to_receiver(self, event: BaseEvent, event_type: type, receiver_id: str) -> None:
        """Publish event to specific receiver subscribers"""
        if event_type not in self._receiver_subscribers:
            return
            
        if receiver_id not in self._receiver_subscribers[event_type]:
            return
            
        live_subscribers = []
        
        for subscriber_ref in self._receiver_subscribers[event_type][receiver_id]:
            subscriber = subscriber_ref()
            if subscriber is not None:
                live_subscribers.append(subscriber_ref)
                try:
                    subscriber(event)
                except Exception as e:
                    print(f"Error in targeted event handler for {receiver_id}: {e}")
                    
        self._receiver_subscribers[event_type][receiver_id] = live_subscribers
    
    def _publish_broadcast(self, event: BaseEvent, event_type: type) -> None:
        """Publish event to all general subscribers"""
        live_subscribers = []
        
        for subscriber_ref in self._subscribers[event_type]:
            subscriber = subscriber_ref()
            if subscriber is not None:
                live_subscribers.append(subscriber_ref)
                try:
                    subscriber(event)
                except Exception as e:
                    print(f"Error in broadcast event handler: {e}")
                    
        self._subscribers[event_type] = live_subscribers
    
    def unsubscribe_receiver(self, receiver_id: str) -> None:
        """Remove all subscriptions for a specific receiver (useful for cleanup)"""
        for event_type in self._receiver_subscribers:
            if receiver_id in self._receiver_subscribers[event_type]:
                del self._receiver_subscribers[event_type][receiver_id]