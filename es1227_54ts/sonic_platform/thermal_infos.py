from sonic_platform_base.sonic_thermal_control.thermal_info_base import ThermalPolicyInfoBase
from sonic_platform_base.sonic_thermal_control.thermal_json_object import thermal_json_object


@thermal_json_object('fan_info')
class FanInfo(ThermalPolicyInfoBase):
    """
    Fan information needed by thermal policy
    """

    # Fan information name
    INFO_NAME = 'fan_info'

    def __init__(self):
        self._absence_fans = set()
        self._presence_fans = set()
        self._fault_fans = set()
        self._status_changed = False

    def collect(self, chassis):
        """
        Collect absence and presence fans.
        :param chassis: The chassis object
        :return:
        """
        self._status_changed = False
        for fan in chassis.get_all_fans():
            status = fan.get_status()
            if fan.get_presence() and fan not in self._presence_fans:
                self._presence_fans.add(fan)
                self._status_changed = True
                if fan in self._absence_fans:
                    self._absence_fans.remove(fan)
            elif not fan.get_presence() and fan not in self._absence_fans:
                self._absence_fans.add(fan)
                self._status_changed = True
                if fan in self._presence_fans:
                    self._presence_fans.remove(fan)

            if not status and fan not in self._fault_fans:
                self._fault_fans.add(fan)
                self._status_changed = True
            elif status and fan in self._fault_fans:
                self._fault_fans.remove(fan)
                self._status_changed = True

    def get_absence_fans(self):
        """
        Retrieves absence fans
        :return: A set of absence fans
        """
        return self._absence_fans

    def get_presence_fans(self):
        """
        Retrieves presence fans
        :return: A set of presence fans
        """
        return self._presence_fans

    def get_fault_fans(self):
        """
        Retrieves fault fans
        :return: A set of fault fans
        """
        return self._fault_fans

    def is_status_changed(self):
        """
        Retrieves if the status of fan information changed
        :return: True if status changed else False
        """
        return self._status_changed


@thermal_json_object('thermal_info')
class ThermalInfo(ThermalPolicyInfoBase):
    """
    Thermal information needed by thermal policy
    """

    # Fan information name
    INFO_NAME = 'thermal_info'

    def __init__(self):
        self._state = ["N/A"] * 15
        self._enter_warm_up_state = [False] * 15
        self.init = False
        self.normal_thres = False
        self.high_thres = False
        self.critical_high_thres = False
        self.warm_up_thres = False
        self._temp_dict = {}

    def collect(self, chassis):
        """
        Collect thermal sensor temperature change status
        :param chassis: The chassis object
        :return:
        """
        # self._cool_down_and_below_low_threshold = False

        # Calculate average temp within the device
        num_of_thermals = chassis.get_num_thermals()

        # Initial the to default
        self.normal_thres = False
        self.high_thres = False
        self.critical_high_thres = False
        self.warm_up_thres = False

        # Collect the information
        for index in range(num_of_thermals):
            if not chassis.get_thermal(index).get_presence():
                continue

            # Store the temperature in the DB
            name = chassis.get_thermal(index).get_name()
            temp = chassis.get_thermal(index).get_temperature()
            self._temp_dict[name] = temp

            # Get the threshold
            normal_temp = chassis.get_thermal(index).get_high_threshold()
            high_temp = chassis.get_thermal(index).get_caution2_threshold()
            critical_high_temp = chassis.get_thermal(index).get_high_critical_threshold()

            # Check if the temperature is over the threshold
            if temp < normal_temp:
                self._state[index] = "n/a"
            elif normal_temp <= temp < high_temp:
                self._state[index] = "normal"
            elif high_temp <= temp < critical_high_temp:
                if self._state[index] == "high":
                    self._enter_warm_up_state[index] = True
                self._state[index] = "high"
            elif temp >= critical_high_temp:
                self._state[index] = "critical"

            # Check the system status
            if self._state[index] == "critical":
                self.critical_high_thres = True
            elif self._state[index] == "high":
                self.high_thres = True
            elif self._state[index] == "normal":
                self.normal_thres = True

            if self._enter_warm_up_state[index]:
                self.warm_up_thres = True

    def get_temp_dict(self):
        return self._temp_dict

    def is_over_high_threshold(self):
        """
        Retrieves if the temperature is over high threshold
        :return: True if the temperature is over high threshold else False
        """
        if self.high_thres and not self.critical_high_thres:
            return True
        return False

    def is_warm_up_and_over_high_threshold(self):
        """
        Retrieves if the temperature is warm up and over high threshold
        :return: True if the temperature is warm up and over high threshold else False
        """

        return self.warm_up_thres

    def is_over_high_critical_threshold(self):
        """
        Retrieves if the temperature is over high critical threshold
        :return: True if the temperature is over high critical threshold else False
        """
        return self.critical_high_thres

    def is_over_normal_threshold(self):
        """
        Retrieves if the temperature is over high critical threshold
        :return: True if the temperature is over high critical threshold else False
        """
        if self.normal_thres and not self.critical_high_thres and not self.high_thres:
            return True
        return False


@thermal_json_object('chassis_info')
class ChassisInfo(ThermalPolicyInfoBase):
    """
    Chassis information needed by thermal policy
    """
    INFO_NAME = 'chassis_info'

    def __init__(self):
        self._chassis = None

    def collect(self, chassis):
        """
        Collect platform chassis.
        :param chassis: The chassis object
        :return:
        """
        self._chassis = chassis

    def get_chassis(self):
        """
        Retrieves platform chassis object
        :return: A platform chassis object.
        """
        return self._chassis
